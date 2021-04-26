copy traveler FROM '/home/data/sample_traveler.csv' DELIMITER ';' CSV HEADER;
copy traveler FROM '/home/data/GeneratedData.csv' DELIMITER ';' CSV HEADER;
copy destination FROM '/home/data/CountryData.csv' DELIMITER ',' CSV HEADER;
