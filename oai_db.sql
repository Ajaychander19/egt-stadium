CREATE DATABASE IF NOT EXISTS oai_db;
USE oai_db;

CREATE TABLE IF NOT EXISTS AuthenticationSubscription (
  ueid VARCHAR(15) PRIMARY KEY,
  authenticationMethod VARCHAR(20),
  encPermanentKey VARCHAR(32),
  protectionParameterId VARCHAR(32),
  sequenceNumber JSON,
  authenticationManagementField VARCHAR(4),
  algorithmId VARCHAR(20),
  encOpcKey VARCHAR(32),
  encTopcKey VARCHAR(32),
  vectorGenerationInHss TINYINT(1),
  n5gcAuthMethod VARCHAR(20),
  rgAuthenticationInd TINYINT(1),
  supi VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS SessionManagementSubscriptionData (
  ueid VARCHAR(15),
  servingPlmnid VARCHAR(15),
  singleNssai JSON,
  dnnConfigurations JSON,
  PRIMARY KEY (ueid, servingPlmnid)
);

-- UE-1: eMBB (SST=1, DNN=oai, 5QI=6)
INSERT IGNORE INTO AuthenticationSubscription VALUES (
  '001010000000001','5G_AKA',
  '0C0A34601D4F07677303652C0462535B',
  '0C0A34601D4F07677303652C0462535B',
  '{"sqn":"000000000020","sqnScheme":"NON_TIME_BASED","lastIndexes":{"ausf":0}}',
  '8000','milenage','63bfa50ee6523365ff14c1f45f88737d',
  NULL,0,NULL,0,'001010000000001'
);
INSERT IGNORE INTO SessionManagementSubscriptionData VALUES (
  '001010000000001','00101',
  '{"sst":1,"sd":"0xFFFFFF"}',
  '{"oai":{"pduSessionTypes":{"defaultSessionType":"IPV4"},"sscModes":{"defaultSscMode":"SSC_MODE_1"},"5gQosProfile":{"5qi":6,"arp":{"priorityLevel":1,"preemptCap":"NOT_PREEMPT","preemptVuln":"NOT_PREEMPTABLE"},"priorityLevel":1},"sessionAmbr":{"uplink":"200Mbps","downlink":"400Mbps"}}}'
);

-- UE-2: URLLC (SST=2, DNN=oai2, 5QI=82)
INSERT IGNORE INTO AuthenticationSubscription VALUES (
  '001010000000002','5G_AKA',
  '0C0A34601D4F07677303652C0462535B',
  '0C0A34601D4F07677303652C0462535B',
  '{"sqn":"000000000020","sqnScheme":"NON_TIME_BASED","lastIndexes":{"ausf":0}}',
  '8000','milenage','63bfa50ee6523365ff14c1f45f88737d',
  NULL,0,NULL,0,'001010000000002'
);
INSERT IGNORE INTO SessionManagementSubscriptionData VALUES (
  '001010000000002','00101',
  '{"sst":2,"sd":"0xFFFFFF"}',
  '{"oai2":{"pduSessionTypes":{"defaultSessionType":"IPV4"},"sscModes":{"defaultSscMode":"SSC_MODE_1"},"5gQosProfile":{"5qi":82,"arp":{"priorityLevel":1,"preemptCap":"NOT_PREEMPT","preemptVuln":"NOT_PREEMPTABLE"},"priorityLevel":1},"sessionAmbr":{"uplink":"50Mbps","downlink":"50Mbps"}}}'
);
