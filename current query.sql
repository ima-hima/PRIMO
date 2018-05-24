SELECT `specimen` .`id`       AS specimen_id,
       `specimen` .`hypocode` AS hypocode,
       `institut` .`instabbr` AS collection_acronym,
       `specimen` .`catlogno` AS catalog_number,
       `taxon`    .`taxoname` AS taxon_name,
       `sex`      .`sex`      AS sex,
       `fossil`   .`fossil`   AS fossil_or_extant,
       `captive`  .`captive`  AS captive_or_wild,
       `original` .`original` AS original_or_cast,
       `variables`.`label`,
       `scalar`   .`value`,
       `session`  .`comments` AS session_comments,
       `specimen` .`comments` AS specimen_comments
FROM `scalar`

Inner Join `variables` ON `scalar`  .`variable_id`  = `variables`.`id`
Inner Join `bpdescxr`  ON `bpdescxr`.`variables_id` = `variables`.`id`
Inner Join `bodypart`  ON `bpdescxr`.`bodypart_id`  = `bodypart` .`id`
Inner Join `session`   ON `scalar`  .`session_id`   = `session`  .`id`
Inner Join `specimen`  ON `session` .`specimen_id`  = `specimen` .`id`
Inner Join `taxon`     ON `specimen`.`taxon_id`     = `taxon`    .`id`
Inner Join `sex`       ON `specimen`.`sex_id`       = `sex`      .`id`
Inner Join `fossil`    ON `specimen`.`fossil_id`    = `fossil`   .`id`
Inner Join `institut`  ON `specimen`.`institut_id`  = `institut` .`id`

ORDER BY `specimen`.`id`, `variables`.`label` ASC

fossil, taxon, variable_id, sex




SELECT DISTINCT `specimen`.`id`          AS specimen_id,
                `specimen`.`hypocode`    AS hypocode,
                `institut`.`instabbr`    AS collection_acronym,
                `specimen`.`catlogno`    AS catalog_number,
                `taxon`   .`taxoname`    AS taxon_name,
                `sex`     .`sex`         AS sex,
                `fossil`  .`fossil`      AS fossil_or_extant,
                `captive` .`captive`     AS captive_or_wild,
                `original`.`original`    AS original_or_cast,
                `protocol`.`label`       AS protocol,
                `session` .`comments`    AS session_comments,
                `specimen`.`comments`    AS specimen_comments,
                `data3d`  .`x`,
                `data3d`  .`y`,
                `data3d`  .`z`,
                `data3d`  .`datindex`,
                `data3d`  .`variable_id`
FROM data3d

Inner Join `variables` ON `data3d`  .`variable_id`  = `variables`.`id`
Inner Join `bpdescxr`  ON `bpdescxr`.`variables_id` = `variables`.`id`
Inner Join `bodypart`  ON `bpdescxr`.`bodypart_id`  = `bodypart` .`id`
Inner Join `session`   ON `data3d`  .`session_id`   = `session`  .`id`
Inner Join `specimen`  ON `session` .`specimen_id`  = `specimen` .`id`
Inner Join `taxon`     ON `specimen`.`taxon_id`     = `taxon`    .`id`
Inner Join `sex`       ON `specimen`.`sex_id`       = `sex`      .`id`
Inner Join `fossil`    ON `specimen`.`fossil_id`    = `fossil`   .`id`
Inner Join `institut`  ON `specimen`.`institut_id`  = `institut` .`id`
Inner Join `protocol`  ON `session` .`protocol_id`  = `protocol` .`id`
Inner Join `captive`   ON `specimen`.`captive_id`   = `captive`  .`id`
Inner Join `original`  ON `session` .`original_id`  = `original` .`id`

ORDER BY `specimen`.`id`, `variables`.`id`, `data3d`.`datindex` ASC

