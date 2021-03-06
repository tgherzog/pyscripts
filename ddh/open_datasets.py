
# this array was build from this spreadsheet:
# https://docs.google.com/spreadsheets/d/16upem6Megcq27dcReEE6bPPMkZH4_idYJRlgaqSXh34/edit#gid=2085715566

open_datasets = [
{'od_id': 1, 'ddh_path': 'world-development-indicators'},
{'od_id': 2, 'ddh_path': 'africa-development-indicators'},
{'od_id': 3, 'ddh_path': 'global-economic-monitor'},
{'od_id': 4, 'ddh_path': ''},
{'od_id': 6, 'ddh_path': 'millennium-development-goals'},
{'od_id': 7, 'ddh_path': 'actionable-governance-indicators'},
{'od_id': 8, 'ddh_path': 'data-statistical-capacity'},
{'od_id': 9, 'ddh_path': 'doing-business'},
{'od_id': 10, 'ddh_path': 'education-statistics'},
{'od_id': 11, 'ddh_path': 'enterprise-surveys'},
{'od_id': 12, 'ddh_path': 'gender-statistics'},
{'od_id': 13, 'ddh_path': 'health-nutrition-and-population-statistics'},
{'od_id': 14, 'ddh_path': 'international-comparison-program-2005'},
{'od_id': 15, 'ddh_path': 'joint-external-debt-hub'},
{'od_id': 16, 'ddh_path': 'logistics-performance-index'},
{'od_id': 17, 'ddh_path': 'private-participation-infrastructure'},
{'od_id': 18, 'ddh_path': 'quarterly-external-debt-statistics-sdds'},
{'od_id': 19, 'ddh_path': 'quarterly-external-debt-statistics-gdds'},
{'od_id': 20, 'ddh_path': ''},
{'od_id': 21, 'ddh_path': 'african-cities-diagnostic'},
{'od_id': 22, 'ddh_path': 'global-financial-development'},
{'od_id': 23, 'ddh_path': 'services-trade-restrictions-database'},
{'od_id': 24, 'ddh_path': 'world-development-report-2013-jobs-statistical-tables'},
{'od_id': 25, 'ddh_path': 'wdr2013-occupational-wages-around-world'},
{'od_id': 26, 'ddh_path': 'wdr2013-survey-good-jobs'},
{'od_id': 27, 'ddh_path': 'worldwide-governance-indicators'},
{'od_id': 28, 'ddh_path': 'privatization-database'},
{'od_id': 29, 'ddh_path': 'ida-results-measurement-system'},
{'od_id': 30, 'ddh_path': ''},
{'od_id': 31, 'ddh_path': 'country-policy-and-institutional-assessment'},
{'od_id': 32, 'ddh_path': 'gem-commodities'},
{'od_id': 33, 'ddh_path': 'remittance-prices-worldwide'},
{'od_id': 35, 'ddh_path': 'temporary-trade-barriers-database-including-global-antidumping-database'},
{'od_id': 36, 'ddh_path': 'gdp-ranking'},
{'od_id': 37, 'ddh_path': 'gdp-ranking-ppp-based'},
{'od_id': 38, 'ddh_path': 'gni-ranking-atlas-method'},
{'od_id': 39, 'ddh_path': 'gni-capita-ranking-atlas-method-and-ppp-based'},
{'od_id': 40, 'ddh_path': ''},
{'od_id': 41, 'ddh_path': ''},
{'od_id': 42, 'ddh_path': ''},
{'od_id': 43, 'ddh_path': 'rural-access-index-rai'},
{'od_id': 44, 'ddh_path': 'business-environment-snapshots'},
{'od_id': 46, 'ddh_path': 'environment-glance-factsheets'},
{'od_id': 50, 'ddh_path': 'education-tables'},
{'od_id': 51, 'ddh_path': 'health-nutrition-population-hnp-lending'},
{'od_id': 52, 'ddh_path': 'population-estimates-and-projections'},
{'od_id': 53, 'ddh_path': 'thematic-health-nutrition-population-hnp-data'},
{'od_id': 54, 'ddh_path': 'millennium-development-goals-tables'},
{'od_id': 55, 'ddh_path': 'country-profiles'},
{'od_id': 56, 'ddh_path': 'world-bank-projects-operations'},
{'od_id': 58, 'ddh_path': ''},
{'od_id': 59, 'ddh_path': 'aidflows'},
{'od_id': 61, 'ddh_path': 'world-integrated-trade-solution-trade-stats'},
{'od_id': 62, 'ddh_path': 'migration-and-remittances-factbook-2011'},
{'od_id': 63, 'ddh_path': 'quarterly-public-sector-debt'},
{'od_id': 64, 'ddh_path': 'changing-wealth-nations'},
{'od_id': 65, 'ddh_path': 'east-asia-and-pacific-economic-update'},
{'od_id': 66, 'ddh_path': 'arab-world-education-performance-indicators'},
{'od_id': 67, 'ddh_path': 'miga-project-portfolio'},
{'od_id': 68, 'ddh_path': ''},
{'od_id': 69, 'ddh_path': 'socio-economic-database-latin-america-and-caribbean'},
{'od_id': 70, 'ddh_path': 'landmine-contamination-casualties-and-clearance-database'},
{'od_id': 71, 'ddh_path': 'world-development-report-2011'},
{'od_id': 73, 'ddh_path': 'global-bilateral-migration-database'},
{'od_id': 74, 'ddh_path': 'population-ranking'},
{'od_id': 75, 'ddh_path': 'bolivia-agricultural-public-expenditure-review'},
{'od_id': 76, 'ddh_path': 'ieg-world-bank-project-performance-ratings'},
{'od_id': 77, 'ddh_path': 'health-nutrition-and-population-statistics-wealth-quintile'},
{'od_id': 78, 'ddh_path': ''},
{'od_id': 79, 'ddh_path': 'haiti-data'},
{'od_id': 80, 'ddh_path': 'climate-change-data'},
{'od_id': 81, 'ddh_path': 'wage-bill-and-pay-compression'},
{'od_id': 82, 'ddh_path': 'climate-change-knowledge-portal-historical-data'},
{'od_id': 83, 'ddh_path': 'little-data-book-climate-change-supplemental-data'},
{'od_id': 84, 'ddh_path': 'climate-development'},
{'od_id': 85, 'ddh_path': 'climate-change-knowledge-portal-ensemble-projections'},
{'od_id': 86, 'ddh_path': 'global-economic-prospects'},
{'od_id': 87, 'ddh_path': 'atlas-social-protection-indicators-resilience-and-equity'},
{'od_id': 88, 'ddh_path': 'global-financial-inclusion-global-findex-database'},
{'od_id': 89, 'ddh_path': 'corporate-scorecard-indicators-2013'},
{'od_id': 90, 'ddh_path': 'exporter-dynamics-database'},
{'od_id': 91, 'ddh_path': 'monitoring-gender-mainstreaming-world-bank-lending-operations'},
{'od_id': 92, 'ddh_path': 'international-debt-statistics'},
{'od_id': 93, 'ddh_path': 'gpe-results-forms-database'},
{'od_id': 94, 'ddh_path': 'escap-world-bank-international-trade-costs'},
{'od_id': 95, 'ddh_path': 'africas-infrastructure-airports'},
{'od_id': 96, 'ddh_path': 'africas-infrastructure-electricity'},
{'od_id': 97, 'ddh_path': 'africas-infrastructure-national-data'},
{'od_id': 98, 'ddh_path': 'africas-infrastructure-ports'},
{'od_id': 99, 'ddh_path': 'africas-infrastructure-railways'},
{'od_id': 100, 'ddh_path': 'africas-infrastructure-wss-utility'},
{'od_id': 101, 'ddh_path': 'sustainable-energy-all'},
{'od_id': 102, 'ddh_path': 'poverty-and-equity-database '},
{'od_id': 103, 'ddh_path': 'service-delivery-indicators'},
{'od_id': 105, 'ddh_path': 'crowd-sourced-price-collection'},
{'od_id': 107, 'ddh_path': 'world-development-report-2014'},
{'od_id': 108, 'ddh_path': 'world-report-disability'},
{'od_id': 109, 'ddh_path': 'public-accountability-mechanisms'},
{'od_id': 110, 'ddh_path': 'subnational-malnutrition-database'},
{'od_id': 111, 'ddh_path': 'wealth-accounting'},
{'od_id': 112, 'ddh_path': 'indonesia-database-policy-and-economic-research'},
{'od_id': 113, 'ddh_path': ''},
{'od_id': 114, 'ddh_path': 'data-resources-structural-economic-analysis'},
{'od_id': 115, 'ddh_path': 'all-ginis-dataset'},
{'od_id': 116, 'ddh_path': 'lac-equity-lab'},
{'od_id': 117, 'ddh_path': ''},
{'od_id': 118, 'ddh_path': 'india-power-sector-review'},
{'od_id': 119, 'ddh_path': 'country-partnership-strategy-india-fy2013-17'},
{'od_id': 120, 'ddh_path': 'jobs'},
{'od_id': 121, 'ddh_path': 'agriculture-africa-telling-facts-myths'},
{'od_id': 122, 'ddh_path': 'subnational-poverty'},
{'od_id': 123, 'ddh_path': 'kenya-boost-public-expenditure-database'},
{'od_id': 124, 'ddh_path': 'armenia-boost-public-expenditure-database'},
{'od_id': 125, 'ddh_path': 'guatemala-boost-public-expenditure-database'},
{'od_id': 126, 'ddh_path': 'kiribati-boost-public-expenditure-database'},
{'od_id': 127, 'ddh_path': 'mexico-boost-public-expenditure-database'},
{'od_id': 128, 'ddh_path': 'minas-gerais-brazil-boost-public-expenditure-database'},
{'od_id': 129, 'ddh_path': 'moldova-boost-public-expenditure-database'},
{'od_id': 130, 'ddh_path': 'paraguay-boost-public-expenditure-database'},
{'od_id': 131, 'ddh_path': 'peru-boost-public-expenditure-database'},
{'od_id': 132, 'ddh_path': 'poland-boost-public-expenditure-database'},
{'od_id': 133, 'ddh_path': 'rio-grande-do-sul-brazil-boost-public-expenditure-database'},
{'od_id': 134, 'ddh_path': 'seychelles-boost-public-expenditure-database'},
{'od_id': 135, 'ddh_path': 'solomon-islands-boost-public-expenditure-database'},
{'od_id': 136, 'ddh_path': 'togo-boost-public-expenditure-database'},
{'od_id': 137, 'ddh_path': 'professional-services-knowledge-platform-africa'},
{'od_id': 138, 'ddh_path': 'export-value-added-database'},
{'od_id': 139, 'ddh_path': 'trade-services-database'},
{'od_id': 140, 'ddh_path': 'gender-highlights-2012-world-development-report'},
{'od_id': 141, 'ddh_path': 'country-partnership-strategy-india-fy2013-17-%C3%A3%C2%90-project-result-indicators-data'},
{'od_id': 142, 'ddh_path': 'comparative-advantage-international-trade-and-fertility'},
{'od_id': 143, 'ddh_path': 'readiness-investment-sustainable-energy'},
{'od_id': 144, 'ddh_path': 'subnational-population-database'},
{'od_id': 148, 'ddh_path': 'public-financial-management-systems-and-eservices-global-dataset'},
{'od_id': 149, 'ddh_path': 'digital-governance-projects-database'},
{'od_id': 150, 'ddh_path': 'fmis-and-open-budget-data-global-dataset'},
{'od_id': 151, 'ddh_path': 'financial-management-information-systems-database'},
{'od_id': 152, 'ddh_path': 'identification-development-global-dataset'},
{'od_id': 153, 'ddh_path': 'costs-meeting-2030-sdg-targets-drinking-water-sanitation-and-hygiene'},
{'od_id': 154, 'ddh_path': 'labor-content-exports-database'},
{'od_id': 155, 'ddh_path': 'sustainable-development-goals'},
{'od_id': 156, 'ddh_path': 'making-power-affordable-africa-and-viable-its-utilities'},
{'od_id': 157, 'ddh_path': 'content-deep-trade-agreements'},
{'od_id': 158, 'ddh_path': 'toolkit-informality-scenario-analysis'},
{'od_id': 159, 'ddh_path': 'tcdata360'},
{'od_id': 160, 'ddh_path': 'africa-development-entrepreneurship'},
{'od_id': 161, 'ddh_path': 'world-bank-procurement-notices'},
{'od_id': 162, 'ddh_path': 'world-bank-contract-awards'},
{'od_id': 163, 'ddh_path': 'g20-financial-inclusion-indicators'},
{'od_id': 164, 'ddh_path': 'commodity-prices-history-and-projections'},
{'od_id': 165, 'ddh_path': 'wdi-database-archives'},
{'od_id': 166, 'ddh_path': ''},
{'od_id': 167, 'ddh_path': 'getting-back-track-reviving-growth-and-securing-prosperity-all-thailand-systematic-country'},
]

