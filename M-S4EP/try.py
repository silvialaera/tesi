# select efficiency table rows
    query = "SELECT input_comm, tech, vintage, output_comm, efficiency FROM Efficiency"
    cursor.execute(query)
    efficiency_rows = cursor.fetchall()

    # filter for valid output
    for i, row in enumerate(efficiency_rows):
        if row[3] not in valid_output and row:
            efficiency_rows.pop(i)

    # join between efficiency and emissionactivity table
    query = "SELECT Efficiency.input_comm, Efficiency.tech, Efficiency.vintage, Efficiency.output_comm, Efficiency.efficiency, EmissionActivity.emis_comm, EmissionActivity.vintage, EmissionActivity.emis_act, EmissionActivity.emis_act_units, EmissionAggregation.emis_agg_weight, EmissionAggregation.emis_agg_units FROM Efficiency, EmissionActivity, EmissionAggregation WHERE Efficiency.tech = EmissionActivity.tech AND EmissionActivity.emis_comm = EmissionAggregation.emis_comm"
    cursor.execute(query)
    efficiency_emissions_rows = cursor.fetchall()
    print(efficiency_emissions_rows)
    # normalise the values
    #for row in efficiency_emissions_rows:
    #    row[7] = normalise_emission_factor_unit(row[7], row[8])

    # calculate global emission activity considering GWP therefore Etot = sum(Ei*GHGi) [ktCO2/tOutput]