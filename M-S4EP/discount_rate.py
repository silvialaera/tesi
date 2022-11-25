import sqlite3
import csv

# Economic parameters for WACC evaluation (Hurdle Rate) (@ 2018)
# HR = WACC = E/E+D*CoE + D/E+D*CoD*(1-CTR) where CoE = RfR + beta_levered*MRP and CoD = EuropeanRfR + CDS

CTR = 24/100
RfR = 2.54/100  # @ 2018
MRP = 9.02/100  # @ 2018
EuropeanRfR = 0.39/100  # @ 2018
CDS = 1.27/100  # @ 2018

# Categories of output commodities are named in accordance with the source for beta
# Chemicals
CH_COM_beta = 0.83  # Commodity chemicals
CH_DIV_beta = 1.13  # Diversified chemicals (Now only methanol)
CH_FER_beta = 1.05  # Fertilizers
CH_GAS_beta = 0.83  # Industrial gases

# Non-metallic minerals
NM_BUI_beta = 1.09  # Building materials
NM_CON_beta = 0.65  # Metals and glass containers

# Pulp and paper
PP_PAP_beta = 1.125  # Paper packaging + paper products

# Non-ferrous metals
NF_ALU_beta = 0.82  # Aluminium
NF_DIV_beta = 1.18  # Diversified metals & mining (Now only Zinc)
NF_COP_beta = 1.12  # Copper

IS_beta = 1.34  # Iron and steel

# Transport
TRA_AVI_beta = 0.78  # Aviation
TRA_NAV_beta = 0.845  # Navigation
TRA_ROA_beta = 0.905  # Public transport and truck of goods
TRA_CAR_beta = 1.61  # Automobile manufacturers
TRA_2WH_beta = 0.92  # Motorcycle manufacturers
TRA_RAIL_beta = 0.745  # Good and passenger rail

beta_group = ["IND_CH_HVC", "IND_CH_BTX", "IND_CH_OLF", "IND_CH_MTH", "IND_CH_AMM", "IND_CH_CHL",
              "IND_NM_CMT", "IND_NM_CLK", "IND_NM_LIM", "IND_NM_CRM", "IND_NM_GLS",
              "IND_PP_PAP", "IND_NF_AMN", "IND_NF_ALU", "IND_NF_ZNC", "IND_NF_COP",
              "IND_IS_BOF", "IND_IS_EAF", "TRA_AVI_DOM", "TRA_AVI_INT",
              "TRA_NAV_DOM", "TRA_NAV_INT", "TRA_ROA_BUS", "TRA_ROA_LCV", "TRA_ROA_HTR", "TRA_ROA_MTR",
              "TRA_ROA_CAR", "TRA_ROA_2WH", "TRA_RAIL_PSG", "TRA_RAIL_FRG"]

beta_value = [CH_COM_beta, CH_COM_beta, CH_COM_beta, CH_DIV_beta, CH_FER_beta, CH_GAS_beta,
              NM_BUI_beta, NM_BUI_beta, NM_BUI_beta, NM_BUI_beta, NM_CON_beta,
              PP_PAP_beta, NF_ALU_beta, NF_ALU_beta, NF_DIV_beta, NF_COP_beta,
              IS_beta, IS_beta, TRA_AVI_beta, TRA_AVI_beta,
              TRA_NAV_beta, TRA_NAV_beta, TRA_ROA_beta, TRA_ROA_beta, TRA_ROA_beta, TRA_ROA_beta,
              TRA_CAR_beta, TRA_2WH_beta, TRA_RAIL_beta, TRA_RAIL_beta]

equity = [75.77, 75.77, 75.77, 69.02, 81.5, 81.5,
          73.93, 73.93, 73.93, 73.93, 73.93,
          75.17, 71.20, 71.20, 71.20, 71.20,
          61.54, 61.54, 56.5, 56.5,
          50.51, 50.51, 50.51, 50.51, 50.51, 50.51,
          38.03, 38.03, 36.69, 36.69]

# vector containing output of tech with HR taken from literature: Not issues for input
output_default = ["COM_CK", "COM_WH", "COM_RF", "COM_SC", "COM_SH", "COM_LG",
                  "RES_CK", "RES_WH", "RES_RF_FRZ", "RES_RF_RFG", "RES_SC", "RES_SH_SO", "RES_SH_MO", "RES_SH_SN", "RES_SH_MN",
                  "RES_CW", "RES_CD", "RES_DW", "RES_LG", "RES_INS_C", "RES_INS_MO", "RES_INS_SN", "RES_INS_SO"]

hr_default = [48, 48, 52, 11, 11, 26,
              48, 48, 52, 52, 11, 11, 11, 11, 11,
              26, 26, 26, 26, 14.75, 14.75, 14.75, 14.75]

heat_pump_output = []
heat_pump_input = []

tra_elc_output = []
tra_elc_input = []

tra_h2_output = []
tra_h2_input = []

elc_output = ["ELC_CEN", "ELC_DST", "HET"]
elc_sol_input = ["ELC_SOL"]


# debt ratio is (1-equity/ratio) they are %
try:
    sqliteConnection = sqlite3.connect('db_prova.sqlite')
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    # create a table with beta, E/D+E, D/D+E values for those categories
    output_values = []
    for i, elem in enumerate(beta_group):
        output = beta_group[i]
        equity_ratio = float(equity[i])/100
        debt_ratio = 1-equity_ratio
        beta = beta_value[i]
        val = str(output) + "-" + str(equity_ratio) + "-" + str(debt_ratio) + "-" + str(beta)
        output_values.append(val)

    # create a table for evaluation of HR
    hurdle_rate_map = dict()
    for i, elem in enumerate(output_values):
        div = elem.split("-")
        output = div[0]
        equity_ratio = div[1]
        debt_ratio = div[2]
        beta = div[3]
        key = output
        value = float(equity_ratio)*(RfR+float(beta)*MRP) + float(debt_ratio)*(1-CTR)*(EuropeanRfR+CDS)
        if key not in hurdle_rate_map.keys():
            hurdle_rate_map.update({key: value})






except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)