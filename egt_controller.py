import json, logging, time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [EGT] %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("egt")

@dataclass
class SystemParams:
    M1: int = 800;   M2: int = 200
    rho_embb: float  = 10.0;  rho_urllc: float = 25.0
    t_prop_mec: float= 0.25;  t_prop_cc: float  = 1.0
    C_cap_mec: float = 13_000.0; C_cap_cc: float= 40_000.0
    k_mec: float= 4.89; k_cc: float= 0.49
    beta: float= 1.0; a: float= 2.0; epsilon: float= 0.01
    PDB_embb: float= 300.0; PDB_urllc: float= 10.0
    phase_multipliers: Dict = field(default_factory=lambda:{1:1.0,2:5.5,3:0.3})

    @property
    def rhos(self):   return [self.rho_embb, self.rho_urllc]
    @property
    def Ms(self):     return [self.M1, self.M2]
    @property
    def C_caps(self): return [self.C_cap_mec, self.C_cap_cc]
    @property
    def ks(self):     return [self.k_mec, self.k_cc]
    @property
    def t_props(self):return [self.t_prop_mec, self.t_prop_cc]
    @property
    def PDBs(self):   return [self.PDB_embb, self.PDB_urllc]

class EGTController:
    GROUP_NAMES = ["eMBB", "URLLC"]
    UPF_NAMES   = ["UPF-MEC", "UPF-CC"]

    def __init__(self, params=None, smf_base_url=None):
        self.p   = params or SystemParams()
        self.smf = smf_base_url
        self.x   = np.full((2, 2), 0.5)

    def rho_norm(self, upf_idx, x, load_mult=1.0):
        load = sum(self.p.rhos[g] * self.p.Ms[g] * x[g, upf_idx] for g in range(2))
        return load * load_mult / self.p.C_caps[upf_idx]

    def upf_delay(self, upf_idx, x, load_mult=1.0):
        return float(np.exp(self.p.ks[upf_idx] * self.rho_norm(upf_idx, x, load_mult)))

    def e2e_delay(self, group, upf_idx, x, load_mult=1.0):
        return self.p.t_props[upf_idx] + self.upf_delay(upf_idx, x, load_mult)

    def payoff(self, group, upf_idx, x, load_mult=1.0):
        return 1.0 / max(self.e2e_delay(group, upf_idx, x, load_mult), 1e-12)

    def step(self, x, load_mult, dt=1.0):
        x_new = x.copy()
        for g in range(2):
            u     = np.array([self.payoff(g, i, x, load_mult) for i in range(2)])
            u_bar = float(np.dot(x[g], u))
            dx    = self.p.beta * (u - u_bar) * x[g]
            x_new[g] = np.clip(x[g] + dx * dt, 1e-6, 1-1e-6)
            x_new[g] /= x_new[g].sum()
        return x_new

    def converged(self, x, load_mult):
        for g in range(2):
            u = np.array([self.payoff(g, i, x, load_mult) for i in range(2)])
            if np.max(np.abs(u - u.mean())) > self.p.epsilon:
                return False
        return True

    def run_to_equilibrium(self, load_mult=1.0, max_iter=300, dt=1.0):
        x = self.x.copy()
        traj, delays = [x.copy()], []
        for it in range(max_iter):
            delays.append([[self.e2e_delay(g, i, x, load_mult)
                            for i in range(2)] for g in range(2)])
            x = self.step(x, load_mult, dt)
            traj.append(x.copy())
            if self.converged(x, load_mult):
                log.debug(f"Converged iter {it+1}")
                break
        self.x = x
        return {"trajectories": np.array(traj), "delays": np.array(delays),
                "equilibrium": x.copy(), "n_iter": len(traj)-1, "load_mult": load_mult}

    def count_violations(self, x, load_mult):
        return {name: sum(int(x[g,i]*self.p.Ms[g])
                for i in range(2)
                if self.e2e_delay(g,i,x,load_mult) > self.p.PDBs[g])
                for g, name in enumerate(self.GROUP_NAMES)}

    def steer(self, slice_group):
        idx = int(np.argmax(self.x[slice_group]))
        return self.UPF_NAMES[idx], float(self.x[slice_group, idx])

    def poll_smf(self):
        if not self.smf:
            return False
        try:
            import requests
            r = requests.get(f"{self.smf}/nsmf-pdusession/v1/sm-contexts", timeout=2.0)
            if r.status_code not in (200, 204):
                return False
            sessions = r.json() if r.content else []
            counts = {"eMBB":[0,0], "URLLC":[0,0]}
            for s in sessions:
                sst = s.get("snssai",{}).get("sst",1)
                upf_ip = (s.get("upfInfo",{}).get("sNssaiUpfInfoList",[{}])[0]
                           .get("dnnUpfInfoList",[{}])[0]
                           .get("upfIpAddress",{}).get("ipv4Address",""))
                g = "eMBB" if sst==1 else "URLLC"
                counts[g][0 if "140" in upf_ip else 1] += 1
            for g, name in enumerate(self.GROUP_NAMES):
                total = sum(counts[name])
                if total > 0:
                    self.x[g] = np.array(counts[name], dtype=float) / total
            log.info(f"SMF poll OK: {counts}")
            return True
        except Exception as e:
            log.debug(f"SMF poll fallback: {e}")
            return False

    def status(self, load_mult=1.0):
        return {"x_eMBB_MEC": round(float(self.x[0,0]),4),
                "x_eMBB_CC":  round(float(self.x[0,1]),4),
                "x_URLLC_MEC":round(float(self.x[1,0]),4),
                "x_URLLC_CC": round(float(self.x[1,1]),4),
                "d_eMBB_MEC": round(self.e2e_delay(0,0,self.x,load_mult),3),
                "d_eMBB_CC":  round(self.e2e_delay(0,1,self.x,load_mult),3),
                "d_URLLC_MEC":round(self.e2e_delay(1,0,self.x,load_mult),3),
                "d_URLLC_CC": round(self.e2e_delay(1,1,self.x,load_mult),3)}
