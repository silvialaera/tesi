import pandas as pd
import numpy as np
import sqlite3

database_name = "TEMOA_Italy.sqlite"
years = np.array([2007, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2025, 2030, 2040, 2050])

# Following 4 lines should be used to set the export results.
# Set the flags to 1 to split by technologies/commodities, to 0 to not split.
# Set to_excel_flag to 1 to export data into a Excel file
# The arrays are used to select the technologies/commodities that should be considered.



technologies_flag = 1
to_excel_flag = 1

technologies = ['COM_LG_INC_N',
'COM_LG_SHAL_STD_N',
'COM_LG_HAL_IMP_N',
'COM_LG_SFL_N',
'COM_LG_LFL_N',
'COM_LG_CFL_N',
'COM_LG_KER_N',
'COM_LG_MER_N',
'COM_LG_SOD_N',
'COM_WH_DST_N',
'COM_WH_COND_DST_N',
'COM_WH_NGA_N',
'COM_WH_COND_NGA_N',
'COM_WH_LPG_N',
'COM_WH_COND_LPG_N',
'COM_WH_WPEL_BIO_N',
'COM_WH_ELC_N',
'COM_WH_AHP_ELC_N',
'COM_WH_HEX_HET_N',
'COM_WH_SOL_N',
'COM_SH_DST_N',
'COM_SH_COND_DST_N',
'COM_SH_NGA_N',
'COM_SH_COND_NGA_N',
'COM_SH_LPG_N',
'COM_SH_COND_LPG_N',
'COM_SH_HEX_HET_N',
'COM_SH_HP_AIR_N',
'COM_SH_HP_PRB_N',
'COM_SH_HP_N',
'COM_SH_GEO_N',
'COM_SH_DST_SOL_N',
'COM_SH_LPG_SOL_N',
'COM_SH_NGA_SOL_N',
'COM_SH_WPEL_N',
'COM_SC_DST_STD_N',
'COM_SC_DST_N',
'COM_SC_HP_STD_N',
'COM_SC_HP_IMP_N',
'COM_SC_ROOF_STD_N',
'COM_SC_ELC_GEO_IMP_N',
'COM_SC_ELC_GEO_ADV_N',
'COM_SC_ROOF_ADV_N',
'COM_SC_REC_N',
'COM_SC_REC_IMP_N',
'COM_SC_CNF_N',
'COM_SC_CNF_IMP_N',
'COM_SC_CNT_N',
'COM_SC_ROOM_N',
'COM_SC_GEO_IMP_N',
'COM_SC_ABS_NGA_N',
'COM_SC_NGA_STD_N',
'COM_SC_NGA_IMP_N',
'COM_CK_NGA_N',
'COM_CK_KER_N',
'COM_CK_LPG_N',
'COM_CK_DST_N',
'COM_CK_ELC_N',
'COM_CK_BIO_N',
'COM_OE_OFF_ELC_STD_N',
'COM_OE_OFF_ELC_IMP_N',
'COM_OE_OFF_ADV_N',
'COM_RF_STD_N',
'COM_RF_IMP_N',
'COM_RF_N']



tech = list()
cost_investment_2007 = list()
cost_investment_2008 = list()
cost_investment_2010 = list()
cost_investment_2012 = list()
cost_investment_2014 = list()
cost_investment_2016 = list()
cost_investment_2018 = list()
cost_investment_2020 = list()
cost_investment_2022 = list()
cost_investment_2025 = list()
cost_investment_2030 = list()
cost_investment_2040 = list()
cost_investment_2050 = list()



# Cost Investment



if technologies_flag == 1:
    for i_tech in range(0, len(technologies)):
        conn = sqlite3.connect(database_name)
        UndiscountedInvestmentCost = pd.read_sql("select * from Output_Costs where output_name = 'V_UndiscountedInvestmentByProcess' and tech = '" + technologies[i_tech] + "'", conn)
        conn.close()
        cost_investment = np.zeros_like(years, dtype=float)
        for i_year in range(0, len(years)):
            for i in range(0, len(UndiscountedInvestmentCost.vintage)):
                if years[i_year] == UndiscountedInvestmentCost.vintage[i]:
                    cost_investment[i_year] = cost_investment[i_year] + UndiscountedInvestmentCost.output_cost[i]
        tech.append(technologies[i_tech])
        cost_investment_2007.append(cost_investment[0])
        cost_investment_2008.append(cost_investment[1])
        cost_investment_2010.append(cost_investment[2])
        cost_investment_2012.append(cost_investment[3])
        cost_investment_2014.append(cost_investment[4])
        cost_investment_2016.append(cost_investment[5])
        cost_investment_2018.append(cost_investment[6])
        cost_investment_2020.append(cost_investment[7])
        cost_investment_2022.append(cost_investment[8])
        cost_investment_2025.append(cost_investment[9])
        cost_investment_2030.append(cost_investment[10])
        cost_investment_2040.append(cost_investment[11])
        cost_investment_2050.append(cost_investment[12])

else:
    cost_investment = np.zeros_like(years, dtype=float)
    for i_tech in range(0, len(technologies)):
        conn = sqlite3.connect(database_name)
        UndiscountedInvestmentCost = pd.read_sql("select * from Output_Costs where output_name = 'V_UndiscountedInvestmentByProcess' and tech = '" + technologies[i_tech] + "'", conn)
        conn.close()
        for i_year in range(0, len(years)):
            for i in range(0, len(UndiscountedInvestmentCost.vintage)):
                if years[i_year] == UndiscountedInvestmentCost.vintage[i]:
                    cost_investment[i_year] = cost_investment[i_year] + UndiscountedInvestmentCost.output_cost[i]
    tech.append('')
    cost_investment_2007.append(cost_investment[0])
    cost_investment_2008.append(cost_investment[1])
    cost_investment_2010.append(cost_investment[2])
    cost_investment_2012.append(cost_investment[3])
    cost_investment_2014.append(cost_investment[4])
    cost_investment_2016.append(cost_investment[5])
    cost_investment_2018.append(cost_investment[6])
    cost_investment_2020.append(cost_investment[7])
    cost_investment_2022.append(cost_investment[8])
    cost_investment_2025.append(cost_investment[9])
    cost_investment_2030.append(cost_investment[10])
    cost_investment_2040.append(cost_investment[11])
    cost_investment_2050.append(cost_investment[12])

# To find rows with only zero elements
delete_index = list()
for i_tech in range(0, len(tech)):
    flag_zero = 0
    if cost_investment_2007[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2008[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2010[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2012[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2014[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2016[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2018[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2020[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2022[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2025[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2030[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2040[i_tech] != 0:
        flag_zero = 1
    elif cost_investment_2050[i_tech] != 0:
        flag_zero = 1

    if flag_zero == 0:
        delete_index.append(i_tech)

# To remove rows with only zeros elements
for i_delete in range(0, len(delete_index)):
    tech.pop(delete_index[i_delete])
    cost_investment_2007.pop(delete_index[i_delete])
    cost_investment_2008.pop(delete_index[i_delete])
    cost_investment_2010.pop(delete_index[i_delete])
    cost_investment_2012.pop(delete_index[i_delete])
    cost_investment_2014.pop(delete_index[i_delete])
    cost_investment_2016.pop(delete_index[i_delete])
    cost_investment_2018.pop(delete_index[i_delete])
    cost_investment_2020.pop(delete_index[i_delete])
    cost_investment_2022.pop(delete_index[i_delete])
    cost_investment_2025.pop(delete_index[i_delete])
    cost_investment_2030.pop(delete_index[i_delete])
    cost_investment_2040.pop(delete_index[i_delete])
    cost_investment_2050.pop(delete_index[i_delete])

    for j_delete in range(0, len(delete_index)):
        delete_index[j_delete] = delete_index[j_delete] - 1

# Building and printing the table
cost_investment_DF = pd.DataFrame(
    {
        "tech": pd.Series(tech, dtype='str'),
        "2007": pd.Series(cost_investment_2007, dtype='float'),
        "2008": pd.Series(cost_investment_2008, dtype='float'),
        "2010": pd.Series(cost_investment_2010, dtype='float'),
        "2012": pd.Series(cost_investment_2012, dtype='float'),
        "2014": pd.Series(cost_investment_2014, dtype='float'),
        "2016": pd.Series(cost_investment_2016, dtype='float'),
        "2018": pd.Series(cost_investment_2018, dtype='float'),
        "2020": pd.Series(cost_investment_2020, dtype='float'),
        "2022": pd.Series(cost_investment_2022, dtype='float'),
        "2025": pd.Series(cost_investment_2025, dtype='float'),
        "2030": pd.Series(cost_investment_2030, dtype='float'),
        "2040": pd.Series(cost_investment_2040, dtype='float'),
        "2050": pd.Series(cost_investment_2050, dtype='float'),
    }
)

pd.set_option('display.max_rows', len(cost_investment_DF))
pd.set_option('display.max_columns', 16)
pd.set_option('display.precision', 2)
pd.set_option('display.float_format', '{:5,.2f}'.format)
print(cost_investment_DF)
print("\n")
pd.reset_option('display.max_rows')



# CostFixed



tech = list()
cost_fixed_2007 = list()
cost_fixed_2008 = list()
cost_fixed_2010 = list()
cost_fixed_2012 = list()
cost_fixed_2014 = list()
cost_fixed_2016 = list()
cost_fixed_2018 = list()
cost_fixed_2020 = list()
cost_fixed_2022 = list()
cost_fixed_2025 = list()
cost_fixed_2030 = list()
cost_fixed_2040 = list()
cost_fixed_2050 = list()

if technologies_flag == 1:
    for i_tech in range(0, len(technologies)):
        conn = sqlite3.connect(database_name)
        UndiscountedFixedCost = pd.read_sql("select * from Output_Costs where output_name = 'V_UndiscountedFixedCostsByProcess' and tech = '" + technologies[i_tech] + "'", conn)
        conn.close()
        cost_fixed = np.zeros_like(years, dtype=float)
        for i_year in range(0, len(years)):
            for i in range(0, len(UndiscountedFixedCost.vintage)):
                if years[i_year] == UndiscountedFixedCost.vintage[i]:
                    cost_fixed[i_year] = cost_fixed[i_year] + UndiscountedFixedCost.output_cost[i]
        tech.append(technologies[i_tech])
        cost_fixed_2007.append(cost_fixed[0])
        cost_fixed_2008.append(cost_fixed[1])
        cost_fixed_2010.append(cost_fixed[2])
        cost_fixed_2012.append(cost_fixed[3])
        cost_fixed_2014.append(cost_fixed[4])
        cost_fixed_2016.append(cost_fixed[5])
        cost_fixed_2018.append(cost_fixed[6])
        cost_fixed_2020.append(cost_fixed[7])
        cost_fixed_2022.append(cost_fixed[8])
        cost_fixed_2025.append(cost_fixed[9])
        cost_fixed_2030.append(cost_fixed[10])
        cost_fixed_2040.append(cost_fixed[11])
        cost_fixed_2050.append(cost_fixed[12])

else:
    cost_fixed = np.zeros_like(years, dtype=float)
    for i_tech in range(0, len(technologies)):
        conn = sqlite3.connect(database_name)
        UndiscountedFixedCost = pd.read_sql("select * from Output_Costs where output_name = 'V_UndiscountedInvestmentByProcess' and tech = '" + technologies[i_tech] + "'", conn)
        conn.close()
        for i_year in range(0, len(years)):
            for i in range(0, len(UndiscountedFixedCost.vintage)):
                if years[i_year] == UndiscountedFixedCost.vintage[i]:
                    cost_fixed[i_year] = cost_fixed[i_year] + UndiscountedFixedCost.output_cost[i]
    tech.append('')
    cost_fixed_2007.append(cost_fixed[0])
    cost_fixed_2008.append(cost_fixed[1])
    cost_fixed_2010.append(cost_fixed[2])
    cost_fixed_2012.append(cost_fixed[3])
    cost_fixed_2014.append(cost_fixed[4])
    cost_fixed_2016.append(cost_fixed[5])
    cost_fixed_2018.append(cost_fixed[6])
    cost_fixed_2020.append(cost_fixed[7])
    cost_fixed_2022.append(cost_fixed[8])
    cost_fixed_2025.append(cost_fixed[9])
    cost_fixed_2030.append(cost_fixed[10])
    cost_fixed_2040.append(cost_fixed[11])
    cost_fixed_2050.append(cost_fixed[12])

# To find rows with only zero elements
delete_index = list()
for i_tech in range(0, len(tech)):
    flag_zero = 0
    if cost_fixed_2007[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2008[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2010[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2012[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2014[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2016[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2018[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2020[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2022[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2025[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2030[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2040[i_tech] != 0:
        flag_zero = 1
    elif cost_fixed_2050[i_tech] != 0:
        flag_zero = 1

    if flag_zero == 0:
        delete_index.append(i_tech)

# To remove rows with only zeros elements
for i_delete in range(0, len(delete_index)):
    tech.pop(delete_index[i_delete])
    cost_fixed_2007.pop(delete_index[i_delete])
    cost_fixed_2008.pop(delete_index[i_delete])
    cost_fixed_2010.pop(delete_index[i_delete])
    cost_fixed_2012.pop(delete_index[i_delete])
    cost_fixed_2014.pop(delete_index[i_delete])
    cost_fixed_2016.pop(delete_index[i_delete])
    cost_fixed_2018.pop(delete_index[i_delete])
    cost_fixed_2020.pop(delete_index[i_delete])
    cost_fixed_2022.pop(delete_index[i_delete])
    cost_fixed_2025.pop(delete_index[i_delete])
    cost_fixed_2030.pop(delete_index[i_delete])
    cost_fixed_2040.pop(delete_index[i_delete])
    cost_fixed_2050.pop(delete_index[i_delete])

    for j_delete in range(0, len(delete_index)):
        delete_index[j_delete] = delete_index[j_delete] - 1

# Building and printing the table
cost_fixed_DF = pd.DataFrame(
    {
        "tech": pd.Series(tech, dtype='str'),
        "2007": pd.Series(cost_fixed_2007, dtype='float'),
        "2008": pd.Series(cost_fixed_2008, dtype='float'),
        "2010": pd.Series(cost_fixed_2010, dtype='float'),
        "2012": pd.Series(cost_fixed_2012, dtype='float'),
        "2014": pd.Series(cost_fixed_2014, dtype='float'),
        "2016": pd.Series(cost_fixed_2016, dtype='float'),
        "2018": pd.Series(cost_fixed_2018, dtype='float'),
        "2020": pd.Series(cost_fixed_2020, dtype='float'),
        "2022": pd.Series(cost_fixed_2022, dtype='float'),
        "2025": pd.Series(cost_fixed_2025, dtype='float'),
        "2030": pd.Series(cost_fixed_2030, dtype='float'),
        "2040": pd.Series(cost_fixed_2040, dtype='float'),
        "2050": pd.Series(cost_fixed_2050, dtype='float'),
    }
)

pd.set_option('display.max_rows', len(cost_fixed_DF))
pd.set_option('display.max_columns', 16)
pd.set_option('display.precision', 2)
pd.set_option('display.float_format', '{:5,.2f}'.format)
print(cost_fixed_DF)
print("\n")
pd.reset_option('display.max_rows')



# CostVariable



tech = list()
cost_variable_2007 = list()
cost_variable_2008 = list()
cost_variable_2010 = list()
cost_variable_2012 = list()
cost_variable_2014 = list()
cost_variable_2016 = list()
cost_variable_2018 = list()
cost_variable_2020 = list()
cost_variable_2022 = list()
cost_variable_2025 = list()
cost_variable_2030 = list()
cost_variable_2040 = list()
cost_variable_2050 = list()

if technologies_flag == 1:
    for i_tech in range(0, len(technologies)):
        conn = sqlite3.connect(database_name)
        UndiscountedVariableCost = pd.read_sql("select * from Output_Costs where output_name = 'V_UndiscountedVariableCostsByProcess' and tech = '" + technologies[i_tech] + "'", conn)
        conn.close()
        cost_variable = np.zeros_like(years, dtype=float)
        for i_year in range(0, len(years)):
            for i in range(0, len(UndiscountedVariableCost.vintage)):
                if years[i_year] == UndiscountedVariableCost.vintage[i]:
                    cost_variable[i_year] = cost_variable[i_year] + UndiscountedVariableCost.output_cost[i]
        tech.append(technologies[i_tech])
        cost_variable_2007.append(cost_variable[0])
        cost_variable_2008.append(cost_variable[1])
        cost_variable_2010.append(cost_variable[2])
        cost_variable_2012.append(cost_variable[3])
        cost_variable_2014.append(cost_variable[4])
        cost_variable_2016.append(cost_variable[5])
        cost_variable_2018.append(cost_variable[6])
        cost_variable_2020.append(cost_variable[7])
        cost_variable_2022.append(cost_variable[8])
        cost_variable_2025.append(cost_variable[9])
        cost_variable_2030.append(cost_variable[10])
        cost_variable_2040.append(cost_variable[11])
        cost_variable_2050.append(cost_variable[12])

else:
    cost_variable = np.zeros_like(years, dtype=float)
    for i_tech in range(0, len(technologies)):
        conn = sqlite3.connect(database_name)
        UndiscountedVariableCost = pd.read_sql("select * from Output_Costs where output_name = 'V_UndiscountedInvestmentByProcess' and tech = '" + technologies[i_tech] + "'", conn)
        conn.close()
        for i_year in range(0, len(years)):
            for i in range(0, len(UndiscountedVariableCost.vintage)):
                if years[i_year] == UndiscountedVariableCost.vintage[i]:
                    cost_variable[i_year] = cost_variable[i_year] + UndiscountedVariableCost.output_cost[i]
    tech.append('')
    cost_variable_2007.append(cost_variable[0])
    cost_variable_2008.append(cost_variable[1])
    cost_variable_2010.append(cost_variable[2])
    cost_variable_2012.append(cost_variable[3])
    cost_variable_2014.append(cost_variable[4])
    cost_variable_2016.append(cost_variable[5])
    cost_variable_2018.append(cost_variable[6])
    cost_variable_2020.append(cost_variable[7])
    cost_variable_2022.append(cost_variable[8])
    cost_variable_2025.append(cost_variable[9])
    cost_variable_2030.append(cost_variable[10])
    cost_variable_2040.append(cost_variable[11])
    cost_variable_2050.append(cost_variable[12])

# To find rows with only zero elements
delete_index = list()
for i_tech in range(0, len(tech)):
    flag_zero = 0
    if cost_variable_2007[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2008[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2010[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2012[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2014[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2016[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2018[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2020[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2022[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2025[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2030[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2040[i_tech] != 0:
        flag_zero = 1
    elif cost_variable_2050[i_tech] != 0:
        flag_zero = 1

    if flag_zero == 0:
        delete_index.append(i_tech)

# To remove rows with only zeros elements
for i_delete in range(0, len(delete_index)):
    tech.pop(delete_index[i_delete])
    cost_variable_2007.pop(delete_index[i_delete])
    cost_variable_2008.pop(delete_index[i_delete])
    cost_variable_2010.pop(delete_index[i_delete])
    cost_variable_2012.pop(delete_index[i_delete])
    cost_variable_2014.pop(delete_index[i_delete])
    cost_variable_2016.pop(delete_index[i_delete])
    cost_variable_2018.pop(delete_index[i_delete])
    cost_variable_2020.pop(delete_index[i_delete])
    cost_variable_2022.pop(delete_index[i_delete])
    cost_variable_2025.pop(delete_index[i_delete])
    cost_variable_2030.pop(delete_index[i_delete])
    cost_variable_2040.pop(delete_index[i_delete])
    cost_variable_2050.pop(delete_index[i_delete])

    for j_delete in range(0, len(delete_index)):
        delete_index[j_delete] = delete_index[j_delete] - 1

# Building and printing the table
cost_variable_DF = pd.DataFrame(
    {
        "tech": pd.Series(tech, dtype='str'),
        "2007": pd.Series(cost_variable_2007, dtype='float'),
        "2008": pd.Series(cost_variable_2008, dtype='float'),
        "2010": pd.Series(cost_variable_2010, dtype='float'),
        "2012": pd.Series(cost_variable_2012, dtype='float'),
        "2014": pd.Series(cost_variable_2014, dtype='float'),
        "2016": pd.Series(cost_variable_2016, dtype='float'),
        "2018": pd.Series(cost_variable_2018, dtype='float'),
        "2020": pd.Series(cost_variable_2020, dtype='float'),
        "2022": pd.Series(cost_variable_2022, dtype='float'),
        "2025": pd.Series(cost_variable_2025, dtype='float'),
        "2030": pd.Series(cost_variable_2030, dtype='float'),
        "2040": pd.Series(cost_variable_2040, dtype='float'),
        "2050": pd.Series(cost_variable_2050, dtype='float'),
    }
)

pd.set_option('display.max_rows', len(cost_variable_DF))
pd.set_option('display.max_columns', 16)
pd.set_option('display.precision', 2)
pd.set_option('display.float_format', '{:5,.2f}'.format)
print(cost_variable_DF)
print("\n")
pd.reset_option('display.max_rows')



# Save to Excel



if to_excel_flag == 1:
    writer = pd.ExcelWriter('Cost.xlsx', engine='xlsxwriter')
    cost_investment_DF.to_excel(writer, sheet_name='Investment Cost')
    cost_fixed_DF.to_excel(writer, sheet_name='Fixed Cost')
    cost_variable_DF.to_excel(writer, sheet_name='Variable Cost')
    writer.save()