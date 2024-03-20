-- MySQL dump 10.13  Distrib 8.0.22, for macos10.15 (x86_64)
--
-- Host: localhost    Database: nyceporg_primo3
-- ------------------------------------------------------
-- Server version	8.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `age_class`
--

DROP TABLE IF EXISTS `age_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `age_class` (
  `id` int NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci DEFAULT NULL,
  `abbr` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `bodypart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bodypart` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `comments` text,
  `expand_in_tree` int NOT NULL DEFAULT '0',
  `tree_root` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `bodypart_FI_1` (`parent_id`)
) ENGINE=InnoDB AUTO_INCREMENT=220 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bodypart_variable`
--

DROP TABLE IF EXISTS `bodypart_variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bodypart_variable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `variable_id` int DEFAULT NULL,
  `bodypart_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bpdescxr_FI_1` (`variable_id`),
  KEY `bpdescxr_FI_2` (`bodypart_id`),
  CONSTRAINT `bodypart_variable_ibfk_1` FOREIGN KEY (`bodypart_id`) REFERENCES `bodypart` (`id`),
  CONSTRAINT `bodypart_variable_ibfk_2` FOREIGN KEY (`variable_id`) REFERENCES `variable` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=595 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `captive`
--

DROP TABLE IF EXISTS `captive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `captive` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `abbr` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `continent`
--

DROP TABLE IF EXISTS `continent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `continent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `country`
--

DROP TABLE IF EXISTS `country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `country` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(191) NOT NULL,
  `abbr` varchar(8) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_3d`
--

DROP TABLE IF EXISTS `data_3d`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_3d` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int DEFAULT NULL,
  `variable_id` int DEFAULT NULL,
  `datindex` int DEFAULT NULL,
  `x` double(16,4) DEFAULT NULL,
  `y` double(16,4) DEFAULT NULL,
  `z` double(16,4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `data_3d_FI_1` (`session_id`),
  KEY `data_3d_FI_2` (`variable_id`),
  CONSTRAINT `data_3d_ibfk_1` FOREIGN KEY (`variable_id`) REFERENCES `variable` (`id`),
  CONSTRAINT `data_3d_ibfk_2` FOREIGN KEY (`session_id`) REFERENCES `session` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=350197 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_scalar`
--

DROP TABLE IF EXISTS `data_scalar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_scalar` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int DEFAULT NULL,
  `variable_id` int DEFAULT NULL,
  `value` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scalar_FI_1` (`session_id`),
  KEY `scalar_FI_2` (`variable_id`),
  CONSTRAINT `data_scalar_ibfk_1` FOREIGN KEY (`variable_id`) REFERENCES `variable` (`id`),
  CONSTRAINT `data_scalar_ibfk_2` FOREIGN KEY (`session_id`) REFERENCES `session` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=221110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datatype`
--

DROP TABLE IF EXISTS `datatype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datatype` (
  `id` int NOT NULL AUTO_INCREMENT,
  `label` varchar(255) DEFAULT NULL,
  `data_table` varchar(32) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `fossil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fossil` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(16) DEFAULT NULL,
  `abbr` varchar(2) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `institute`
--

DROP TABLE IF EXISTS `institute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `institute` (
  `id` int NOT NULL AUTO_INCREMENT,
  `abbr` varchar(8) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `institute_department` varchar(255) DEFAULT NULL,
  `locality_id` int DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`),
  KEY `institut_FI_1` (`locality_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `laterality`
--

DROP TABLE IF EXISTS `laterality`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `laterality` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `abbr` varchar(1) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `locality`
--

DROP TABLE IF EXISTS `locality`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locality` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `continent_id` int DEFAULT NULL,
  `latitude` double(16,4) DEFAULT NULL,
  `longitude` double(16,4) DEFAULT NULL,
  `comments` text,
  `country_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `locality_FI_2` (`continent_id`),
  KEY `country_id` (`country_id`),
  CONSTRAINT `locality_ibfk_1` FOREIGN KEY (`continent_id`) REFERENCES `continent` (`id`),
  CONSTRAINT `locality_ibfk_2` FOREIGN KEY (`country_id`) REFERENCES `country` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `observer`
--

DROP TABLE IF EXISTS `observer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `observer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `initials` varchar(4) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `original`
--

DROP TABLE IF EXISTS `original`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `original` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(16) DEFAULT NULL,
  `abbr` varchar(2) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paired`
--

DROP TABLE IF EXISTS `paired`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paired` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `abbr` varchar(1) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `primo_authgrouppermissions`
--

DROP TABLE IF EXISTS `protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `protocol` (
  `id` int NOT NULL AUTO_INCREMENT,
  `label` varchar(255) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `protocol_variable`
--

DROP TABLE IF EXISTS `protocol_variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `protocol_variable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `protocol_id` int DEFAULT NULL,
  `variable_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `prdescxr_FI_1` (`protocol_id`),
  KEY `prdescxr_FI_2` (`variable_id`),
  CONSTRAINT `protocol_variable_ibfk_1` FOREIGN KEY (`protocol_id`) REFERENCES `protocol` (`id`),
  CONSTRAINT `protocol_variable_ibfk_2` FOREIGN KEY (`variable_id`) REFERENCES `variable` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=595 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rank`
--

DROP TABLE IF EXISTS `rank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rank` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `session`
--

DROP TABLE IF EXISTS `session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session` (
  `id` int NOT NULL AUTO_INCREMENT,
  `observer_id` int DEFAULT NULL,
  `specimen_id` int DEFAULT NULL,
  `protocol_id` int DEFAULT NULL,
  `iteration` int DEFAULT NULL,
  `comments` text,
  `filename` varchar(255) DEFAULT NULL,
  `group_id` int DEFAULT NULL,
  `original_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `session_FI_1` (`observer_id`),
  KEY `session_FI_2` (`specimen_id`),
  KEY `session_FI_3` (`protocol_id`),
  KEY `session_FI_7` (`group_id`),
  KEY `original_id` (`original_id`),
  CONSTRAINT `session_ibfk_1` FOREIGN KEY (`observer_id`) REFERENCES `observer` (`id`),
  CONSTRAINT `session_ibfk_2` FOREIGN KEY (`specimen_id`) REFERENCES `specimen` (`id`),
  CONSTRAINT `session_ibfk_3` FOREIGN KEY (`protocol_id`) REFERENCES `protocol` (`id`),
  CONSTRAINT `session_ibfk_4` FOREIGN KEY (`original_id`) REFERENCES `original` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21517 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sex`
--

DROP TABLE IF EXISTS `sex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sex` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(16) DEFAULT NULL,
  `abbr` varchar(2) DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `specimen`
--

DROP TABLE IF EXISTS `specimen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `specimen` (
  `id` int NOT NULL,
  `hypocode` varchar(20) DEFAULT NULL,
  `taxon_id` int DEFAULT NULL,
  `institute_id` int DEFAULT NULL,
  `catalog_number` varchar(64) DEFAULT NULL,
  `mass` int DEFAULT NULL,
  `locality_id` int DEFAULT NULL,
  `sex_id` int DEFAULT NULL,
  `age_class_id` int NOT NULL DEFAULT '9',
  `fossil_id` int DEFAULT NULL,
  `captive_id` int DEFAULT NULL,
  `comments` text,
  `specimen_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `specimen_FI_1` (`taxon_id`),
  KEY `specimen_FI_2` (`institute_id`),
  KEY `specimen_FI_3` (`locality_id`),
  KEY `specimen_FI_4` (`sex_id`),
  KEY `specimen_FI_5` (`age_class_id`),
  KEY `specimen_FI_6` (`fossil_id`),
  KEY `specimen_FI_7` (`captive_id`),
  CONSTRAINT `specimen_ibfk_11` FOREIGN KEY (`captive_id`) REFERENCES `captive` (`id`),
  CONSTRAINT `specimen_ibfk_12` FOREIGN KEY (`locality_id`) REFERENCES `locality` (`id`),
  CONSTRAINT `specimen_ibfk_10` FOREIGN KEY (`fossil_id`) REFERENCES `fossil` (`id`),
  CONSTRAINT `specimen_ibfk_9` FOREIGN KEY (`age_class_id`) REFERENCES `age_class` (`id`),
  CONSTRAINT `specimen_ibfk_8` FOREIGN KEY (`taxon_id`) REFERENCES `taxon` (`id`),
  CONSTRAINT `specimen_institute_id_6b74cb65_fk_institute_id` FOREIGN KEY (`institute_id`) REFERENCES `institute` (`id`),
  CONSTRAINT `specimen_sex_id_743ba5d0_fk_sex_id` FOREIGN KEY (`sex_id`) REFERENCES `sex` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `specimen_type`
--

DROP TABLE IF EXISTS `specimen_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `specimen_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `abbr` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `comments` text,
  `createby` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updateby` int DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `type_FI_1` (`createby`),
  KEY `type_FI_2` (`updateby`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taxon`
--

DROP TABLE IF EXISTS `taxon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `taxon` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_id` int DEFAULT NULL,
  `rank_id` int DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `expand_in_tree` tinyint(1) NOT NULL,
  `fossil_id` int NOT NULL,
  `comments` text,
  `tree_root` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `taxon_FI_2` (`rank_id`),
  KEY `taxon_FI_3` (`fossil_id`),
  KEY `taxon_FI_1` (`parent_id`) USING BTREE,
  CONSTRAINT `taxon_ibfk_1` FOREIGN KEY (`rank_id`) REFERENCES `rank` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=762 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `variable`
--

DROP TABLE IF EXISTS `variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `label` varchar(32) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `laterality_id` int DEFAULT NULL,
  `datatype_id` int DEFAULT NULL,
  `paired_with_id` int DEFAULT NULL,
  `comments` text,
  PRIMARY KEY (`id`),
  KEY `variables_FI_1` (`laterality_id`),
  KEY `variables_FI_2` (`datatype_id`),
  KEY `variable_paired_with_id_fc2a9a72_fk_variable_id` (`paired_with_id`),
  CONSTRAINT `variable_ibfk_1` FOREIGN KEY (`datatype_id`) REFERENCES `datatype` (`id`),
  CONSTRAINT `variable_laterality_id_f16630be_fk_laterality_id` FOREIGN KEY (`laterality_id`) REFERENCES `laterality` (`id`),
  CONSTRAINT `variable_paired_with_id_fc2a9a72_fk_variable_id` FOREIGN KEY (`paired_with_id`) REFERENCES `variable` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=639 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-15 15:09:29
