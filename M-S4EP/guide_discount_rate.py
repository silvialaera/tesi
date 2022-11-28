# DiscountRate

conn = sqlite3.connect(database_name)
time_periods = pd.read_sql("select * from time_periods", conn)
DiscountRate = pd.read_sql("select * from DiscountRate", conn)

regions = list()
tech = list()
vintage = list()
tech_rate = list()
tech_rate_notes = list()

tech_already_considered = list()
for i_tech in range(0, len(DiscountRate.tech)):
    tech_i = DiscountRate.tech[i_tech]

    flag_check = 0
    tech_i_check = tech_i
    for check in range(0, len(tech_already_considered)):
        if tech_i_check == tech_already_considered[check]:
            flag_check = 1

    if flag_check == 0:
        # Checking if other values are present for the technology
        flag = 0
        location = list()
        location.append(i_tech)
        for j_tech in range(i_tech + 1, len(DiscountRate.tech)):
            tech_j_check = DiscountRate.tech[j_tech]
            if tech_j_check == tech_i_check:
                flag = 1
                location.append(j_tech)
                tech_already_considered.append(tech_i_check)

        if flag == 0:  # No other values
            for i_year in range(0, len(time_periods)):
                if time_periods.t_periods[i_year] >= DiscountRate.vintage[i_tech] and time_periods.t_periods[i_year] != \
                        time_periods.t_periods[len(time_periods.t_periods) - 1]:
                    regions.append(DiscountRate.regions[i_tech])
                    tech.append(DiscountRate.tech[i_tech])
                    vintage.append(int(time_periods.t_periods[i_year]))
                    tech_rate.append(float(np.format_float_scientific(DiscountRate.tech_rate[i_tech], 2)))
                    tech_rate_notes.append(DiscountRate.tech_rate_notes[i_tech])

        else:
            for i_location in range(0, len(location) - 1):
                year1 = DiscountRate.vintage[location[i_location]]
                year2 = DiscountRate.vintage[location[i_location + 1]]
                min_cap1 = DiscountRate.tech_rate[location[i_location]]
                min_cap2 = DiscountRate.tech_rate[location[i_location + 1]]

                for i_year in range(0, len(time_periods)):
                    year = time_periods.t_periods[i_year]
                    if year1 <= year < year2:
                        regions.append(DiscountRate.regions[i_tech])
                        tech.append(DiscountRate.tech[i_tech])
                        vintage.append(int(year))
                        tech_rate.append(float(np.format_float_scientific(min_cap1 + (year - year1) / (year2 - year1) * (min_cap2 - min_cap1), 2)))
                        tech_rate_notes.append(DiscountRate.tech_rate_notes[i_tech])

            year_last = DiscountRate.vintage[location[i_location + 1]]
            min_cap = DiscountRate.tech_rate[location[i_location + 1]]
            if year_last != time_periods.t_periods[len(time_periods.t_periods) - 1]:
                for i_year in range(0, len(time_periods.t_periods)):
                    year = time_periods.t_periods[i_year]
                    if year >= year_last and year != time_periods.t_periods[len(time_periods.t_periods) - 1]:
                        regions.append(DiscountRate.regions[i_tech])
                        tech.append(DiscountRate.tech[i_tech])
                        vintage.append(int(year))
                        tech_rate.append(float(np.format_float_scientific(DiscountRate.tech_rate[location[i_location + 1]], 2)))
                        tech_rate_notes.append(DiscountRate.tech_rate_notes[i_tech])

DiscountRate_DF = pd.DataFrame(
    {
        "regions": pd.Series(regions, dtype='str'),
        "tech": pd.Series(tech, dtype='str'),
        "vintage": pd.Series(vintage, dtype='int'),
        "tech_rate": pd.Series(tech_rate, dtype='float'),
        "tech_rate_notes": pd.Series(tech_rate_notes, dtype='str')
    }
)

if tosql_set['DiscountRate']:
    DiscountRate_DF.to_sql("DiscountRate", conn, index=False, if_exists='replace')

if print_set['DiscountRate']:
    pd.set_option('display.max_rows', len(DiscountRate_DF))
    pd.set_option('display.max_columns', len(DiscountRate_DF))
    print("\nDiscountRate DataFrame\n\n", DiscountRate_DF)
    pd.reset_option('display.max_rows')

conn.close()
print_i = print_i + 1
if print_i <= 9:
    print('[', print_i, ' /', len(print_set), ']     DiscountRate updated...')
else:
    print('[', print_i, '/', len(print_set), ']     DiscountRate updated...')