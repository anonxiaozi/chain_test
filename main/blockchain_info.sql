-- MySQL dump 10.13  Distrib 8.0.16, for Linux (x86_64)
--
-- Host: 10.15.101.25    Database: gosig
-- ------------------------------------------------------
-- Server version	5.5.5-10.1.31-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `blockchain_info`
--

DROP TABLE IF EXISTS `blockchain_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `blockchain_info` (
  `keyname` varchar(32) NOT NULL,
  `value` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`keyname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blockchain_info`
--

LOCK TABLES `blockchain_info` WRITE;
/*!40000 ALTER TABLE `blockchain_info` DISABLE KEYS */;
INSERT INTO `blockchain_info` VALUES ('MaxAmount',10000000),('MinAmount',1),('NewAccountCost',0),('PeerBlockHeight',5179),('TransferCost',0);
/*!40000 ALTER TABLE `blockchain_info` ENABLE KEYS */;
UNLOCK TABLES;
