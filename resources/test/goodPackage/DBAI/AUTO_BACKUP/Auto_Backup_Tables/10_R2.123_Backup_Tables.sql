------------------------------------------------------------
-- BACKUP TABLES
------------------------------------------------------------
CREATE MULTISET TABLE PDDBABKP.FACT_ACCT_BALN_STG_C1234567 AS P_D_BAL_001_STD_0.FACT_ACCT_BALN_STG WITH DATA AND STATS;

------------------------------------------------------------
-- APPLY COMMENTS
------------------------------------------------------------
COMMENT ON TABLE PDDBABKP.FACT_ACCT_BALN_STG_C1234567 IS 'C1234567:To be dropped on 30-June-2015 - Naga Nandyala. Table origin P_D_BAL_001_STD_0.FACT_ACCT_BALN_STG';
