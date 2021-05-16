copy traveler FROM '/home/data/sample_traveler.csv' DELIMITER ';' CSV HEADER;
copy traveler FROM '/home/data/GeneratedData.csv' DELIMITER ';' CSV HEADER;
copy destination FROM '/home/data/CountryData.csv' DELIMITER ',' CSV HEADER;
copy attractions FROM '/home/data/TouristAttractions.csv' DELIMITER ',' CSV HEADER;
copy attractions FROM '/home/data/TouristAttractionsNP.csv' DELIMITER ',' CSV HEADER;
copy zipcodes FROM '/home/data/zipcodes.csv' DELIMITER ',' CSV HEADER;