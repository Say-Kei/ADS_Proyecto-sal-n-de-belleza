-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: salondebelleza1
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add Cita',7,'add_cita'),(26,'Can change Cita',7,'change_cita'),(27,'Can delete Cita',7,'delete_cita'),(28,'Can view Cita',7,'view_cita'),(29,'Can add Establecimiento',8,'add_establecimiento'),(30,'Can change Establecimiento',8,'change_establecimiento'),(31,'Can delete Establecimiento',8,'delete_establecimiento'),(32,'Can view Establecimiento',8,'view_establecimiento'),(33,'Can add Categoría',9,'add_categoria'),(34,'Can change Categoría',9,'change_categoria'),(35,'Can delete Categoría',9,'delete_categoria'),(36,'Can view Categoría',9,'view_categoria'),(37,'Can add Factura',10,'add_factura'),(38,'Can change Factura',10,'change_factura'),(39,'Can delete Factura',10,'delete_factura'),(40,'Can view Factura',10,'view_factura'),(41,'Can add Detalle de Factura',11,'add_facturadetalle'),(42,'Can change Detalle de Factura',11,'change_facturadetalle'),(43,'Can delete Detalle de Factura',11,'delete_facturadetalle'),(44,'Can view Detalle de Factura',11,'view_facturadetalle'),(45,'Can add Perfil de Usuario',12,'add_perfilusuario'),(46,'Can change Perfil de Usuario',12,'change_perfilusuario'),(47,'Can delete Perfil de Usuario',12,'delete_perfilusuario'),(48,'Can view Perfil de Usuario',12,'view_perfilusuario'),(49,'Can add Horario de Trabajador',13,'add_horariotrabajador'),(50,'Can change Horario de Trabajador',13,'change_horariotrabajador'),(51,'Can delete Horario de Trabajador',13,'delete_horariotrabajador'),(52,'Can view Horario de Trabajador',13,'view_horariotrabajador'),(53,'Can add Reseña',14,'add_resena'),(54,'Can change Reseña',14,'change_resena'),(55,'Can delete Reseña',14,'delete_resena'),(56,'Can view Reseña',14,'view_resena'),(57,'Can add Servicio',15,'add_servicio'),(58,'Can change Servicio',15,'change_servicio'),(59,'Can delete Servicio',15,'delete_servicio'),(60,'Can view Servicio',15,'view_servicio'),(61,'Can add Horario de Establecimiento',16,'add_horarioestablecimiento'),(62,'Can change Horario de Establecimiento',16,'change_horarioestablecimiento'),(63,'Can delete Horario de Establecimiento',16,'delete_horarioestablecimiento'),(64,'Can view Horario de Establecimiento',16,'view_horarioestablecimiento'),(65,'Can add Blacklisted Token',17,'add_blacklistedtoken'),(66,'Can change Blacklisted Token',17,'change_blacklistedtoken'),(67,'Can delete Blacklisted Token',17,'delete_blacklistedtoken'),(68,'Can view Blacklisted Token',17,'view_blacklistedtoken'),(69,'Can add Outstanding Token',18,'add_outstandingtoken'),(70,'Can change Outstanding Token',18,'change_outstandingtoken'),(71,'Can delete Outstanding Token',18,'delete_outstandingtoken'),(72,'Can view Outstanding Token',18,'view_outstandingtoken');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$NhmgyWR6tFBB6YB6ETZGlz$LpwPm1XMLPq6TOiwYuwHfufa6uRqZLq9Mfk0zreQOWo=','2026-09-24 21:36:31.830804',1,'admin','','','admin@gmail.com',1,1,'2026-09-24 21:35:55.829613'),(2,'pbkdf2_sha256$1000000$kUnXm7vyvSO2bRIBnhIl5x$eEd661wb4Y97+DkQUarHQ2ZX8RAkVJ2DK8yOht8Xr10=',NULL,0,'admin_glamour','','','',0,1,'2026-09-24 22:08:14.074955'),(3,'pbkdf2_sha256$1000000$rYZMiPuHpGagKtEDnVPxAQ$FMoUE3bPHBlzUysnJh013RbaT6srjhLaxRYk6EXDymQ=',NULL,0,'valeria_estilista','','','',0,1,'2026-09-24 22:08:51.060972'),(4,'pbkdf2_sha256$1000000$rlW4jwHZjHAL1bf0qVfUya$wg06kFW/yTdKIlMcqdtbZuBouXEIJ4xZrV5R8tAJFq4=',NULL,0,'carlos_barbero','','','',0,1,'2026-09-24 22:09:11.913039');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre_establecimiento` varchar(150) DEFAULT NULL,
  `nombre` varchar(80) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `id_establecimiento` int NOT NULL,
  PRIMARY KEY (`id_categoria`),
  KEY `categoria_id_establecimiento_16e2213c_fk_estableci` (`id_establecimiento`),
  CONSTRAINT `categoria_id_establecimiento_16e2213c_fk_estableci` FOREIGN KEY (`id_establecimiento`) REFERENCES `establecimiento` (`id_establecimiento`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (1,'Glamour & Style Salon','Cuidado Capilar y Peinados',1,1),(2,'Glamour & Style Salon','Manicura y Pedicura',1,1),(3,'Glamour & Style Salon','Estética Facial',1,1);
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cita`
--

DROP TABLE IF EXISTS `cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cita` (
  `id_cita` int NOT NULL AUTO_INCREMENT,
  `nombre_establecimiento` varchar(150) DEFAULT NULL,
  `nombre_cliente` varchar(120) NOT NULL,
  `correo_cliente` varchar(254) NOT NULL,
  `telefono_cliente` varchar(20) NOT NULL,
  `fecha_cita` date NOT NULL,
  `hora_inicio` time(6) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `notas` longtext,
  `creado_el` datetime(6) NOT NULL,
  `id_perfil` int DEFAULT NULL,
  `id_servicio` int NOT NULL,
  PRIMARY KEY (`id_cita`),
  KEY `cita_id_perfil_572f7010_fk_perfil_usuario_id_perfil` (`id_perfil`),
  KEY `cita_id_servicio_7d521265_fk_servicio_id_servicio` (`id_servicio`),
  CONSTRAINT `cita_id_perfil_572f7010_fk_perfil_usuario_id_perfil` FOREIGN KEY (`id_perfil`) REFERENCES `perfil_usuario` (`id_perfil`),
  CONSTRAINT `cita_id_servicio_7d521265_fk_servicio_id_servicio` FOREIGN KEY (`id_servicio`) REFERENCES `servicio` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cita`
--

LOCK TABLES `cita` WRITE;
/*!40000 ALTER TABLE `cita` DISABLE KEYS */;
INSERT INTO `cita` VALUES (1,'Glamour & Style Salon','Marta','marta@gmail.com','3456854','2026-09-26','02:00:00.000000','PENDIENTE','','2026-09-24 23:13:50.497978',2,2);
/*!40000 ALTER TABLE `cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-09-24 22:08:14.386085','2','admin_glamour',1,'[{\"added\": {}}]',4,1),(2,'2026-09-24 22:08:51.373568','3','valeria_estilista',1,'[{\"added\": {}}]',4,1),(3,'2026-09-24 22:09:12.222126','4','carlos_barbero',1,'[{\"added\": {}}]',4,1),(4,'2026-09-24 22:11:28.861207','1','Glamour & Style Salon (NIT: 901234567-8)',1,'[{\"added\": {}}]',8,1),(5,'2026-09-24 22:12:25.922907','1','admin_glamour - Administrador de Negocio (Glamour & Style Salon)',1,'[{\"added\": {}}]',12,1),(6,'2026-09-24 22:13:03.647758','2','valeria_estilista - Trabajador / Esteticista / Peluquero (Glamour & Style Salon)',1,'[{\"added\": {}}]',12,1),(7,'2026-09-24 22:13:36.938129','3','carlos_barbero - Trabajador / Esteticista / Peluquero (Glamour & Style Salon)',1,'[{\"added\": {}}]',12,1),(8,'2026-09-24 22:14:24.964751','1','Lunes (08:00:00 - 19:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(9,'2026-09-24 22:14:40.253754','2','Martes (08:00:00 - 19:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(10,'2026-09-24 22:14:46.796638','3','Miércoles (08:00:00 - 19:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(11,'2026-09-24 22:15:00.716933','4','Jueves (08:00:00 - 19:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(12,'2026-09-24 22:15:07.152623','5','Viernes (08:00:00 - 19:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(13,'2026-09-24 22:15:14.202305','6','Sábado (08:00:00 - 19:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(14,'2026-09-24 22:15:36.870620','7','Domingo (09:00:00 - 14:00:00) - Glamour & Style Salon',1,'[{\"added\": {}}]',16,1),(15,'2026-09-24 22:16:37.327231','1','Turno Lunes - valeria_estilista',1,'[{\"added\": {}}]',13,1),(16,'2026-09-24 22:16:49.425929','2','Turno Martes - valeria_estilista',1,'[{\"added\": {}}]',13,1),(17,'2026-09-24 22:16:58.472365','3','Turno Miércoles - valeria_estilista',1,'[{\"added\": {}}]',13,1),(18,'2026-09-24 22:17:06.890094','4','Turno Jueves - valeria_estilista',1,'[{\"added\": {}}]',13,1),(19,'2026-09-24 22:17:15.977002','5','Turno Viernes - valeria_estilista',1,'[{\"added\": {}}]',13,1),(20,'2026-09-24 22:17:45.154287','6','Turno Sábado - valeria_estilista',1,'[{\"added\": {}}]',13,1),(21,'2026-09-24 22:18:12.865658','7','Turno Domingo - valeria_estilista',1,'[{\"added\": {}}]',13,1),(22,'2026-09-24 22:18:51.908061','1','Cuidado Capilar y Peinados (Glamour & Style Salon)',1,'[{\"added\": {}}]',9,1),(23,'2026-09-24 22:19:03.828365','2','Manicura y Pedicura (Glamour & Style Salon)',1,'[{\"added\": {}}]',9,1),(24,'2026-09-24 22:19:14.819492','3','Estética Facial (Glamour & Style Salon)',1,'[{\"added\": {}}]',9,1),(25,'2026-09-24 22:20:58.817535','1','Corte y Cepillado Dama - $45,000 (Glamour & Style Salon)',1,'[{\"added\": {}}]',15,1),(26,'2026-09-24 22:22:08.406189','2','Uñitas Semipermanentes - $60,000 (Glamour & Style Salon)',1,'[{\"added\": {}}]',15,1),(27,'2026-09-24 22:22:59.641175','3','Corte Caballero y Barba - $30,000 (Glamour & Style Salon)',1,'[{\"added\": {}}]',15,1),(28,'2026-09-24 23:13:50.500287','1','Cita object (1)',1,'[{\"added\": {}}]',7,1),(29,'2026-09-24 23:14:28.575046','1','Factura FAC-9478F68D - Glamour & Style Salon',1,'[{\"added\": {}}]',10,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(9,'agendaSalon','categoria'),(7,'agendaSalon','cita'),(8,'agendaSalon','establecimiento'),(10,'agendaSalon','factura'),(11,'agendaSalon','facturadetalle'),(16,'agendaSalon','horarioestablecimiento'),(13,'agendaSalon','horariotrabajador'),(12,'agendaSalon','perfilusuario'),(14,'agendaSalon','resena'),(15,'agendaSalon','servicio'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session'),(17,'token_blacklist','blacklistedtoken'),(18,'token_blacklist','outstandingtoken');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-09-24 21:35:10.172202'),(2,'auth','0001_initial','2026-09-24 21:35:10.643583'),(3,'admin','0001_initial','2026-09-24 21:35:10.761720'),(4,'admin','0002_logentry_remove_auto_add','2026-09-24 21:35:10.769464'),(5,'admin','0003_logentry_add_action_flag_choices','2026-09-24 21:35:10.777314'),(6,'agendaSalon','0001_initial','2026-09-24 21:35:11.679793'),(7,'contenttypes','0002_remove_content_type_name','2026-09-24 21:35:11.767806'),(8,'auth','0002_alter_permission_name_max_length','2026-09-24 21:35:11.826369'),(9,'auth','0003_alter_user_email_max_length','2026-09-24 21:35:11.852098'),(10,'auth','0004_alter_user_username_opts','2026-09-24 21:35:11.859662'),(11,'auth','0005_alter_user_last_login_null','2026-09-24 21:35:11.917017'),(12,'auth','0006_require_contenttypes_0002','2026-09-24 21:35:11.919756'),(13,'auth','0007_alter_validators_add_error_messages','2026-09-24 21:35:11.927062'),(14,'auth','0008_alter_user_username_max_length','2026-09-24 21:35:11.988206'),(15,'auth','0009_alter_user_last_name_max_length','2026-09-24 21:35:12.045399'),(16,'auth','0010_alter_group_name_max_length','2026-09-24 21:35:12.073131'),(17,'auth','0011_update_proxy_permissions','2026-09-24 21:35:12.122957'),(18,'auth','0012_alter_user_first_name_max_length','2026-09-24 21:35:12.194018'),(19,'sessions','0001_initial','2026-09-24 21:35:12.227838'),(20,'token_blacklist','0001_initial','2026-09-24 21:35:12.376552'),(21,'token_blacklist','0002_outstandingtoken_jti_hex','2026-09-24 21:35:12.421959'),(22,'token_blacklist','0003_auto_20171017_2007','2026-09-24 21:35:12.441537'),(23,'token_blacklist','0004_auto_20171017_2013','2026-09-24 21:35:12.500865'),(24,'token_blacklist','0005_remove_outstandingtoken_jti','2026-09-24 21:35:12.544996'),(25,'token_blacklist','0006_auto_20171017_2113','2026-09-24 21:35:12.569215'),(26,'token_blacklist','0007_auto_20171017_2214','2026-09-24 21:35:12.727279'),(27,'token_blacklist','0008_migrate_to_bigautofield','2026-09-24 21:35:12.918411'),(28,'token_blacklist','0010_fix_migrate_to_bigautofield','2026-09-24 21:35:12.939337'),(29,'token_blacklist','0011_linearizes_history','2026-09-24 21:35:12.942221'),(30,'token_blacklist','0012_alter_outstandingtoken_user','2026-09-24 21:35:12.957972'),(31,'token_blacklist','0013_alter_blacklistedtoken_options_and_more','2026-09-24 21:35:12.970861');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('tazk1b66d7hqpt6z05hi62booxmx098m','.eJxVjMsKwjAQAP9lzxK2eZCkR-9-Q9jNJqYqLTTtSfx3KfSg15lh3pBo31rae1nTJDDCAJdfxpSfZT6EPGi-Lyov87ZOrI5Enbar2yLldT3bv0Gj3mAEQ1GcF3SIhgxrZq1Lphyl-mBrFRxs9p5Lsdn5INUE7TAgo0g0leHzBfZ5OIc:1x9r7H:bvA8S95vjACsvmkMBb5uUBDzQqTpkL7q5ZWOqUEoj6Q','2026-10-08 21:36:31.834474');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `establecimiento`
--

DROP TABLE IF EXISTS `establecimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `establecimiento` (
  `id_establecimiento` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `slug` varchar(160) NOT NULL,
  `descripcion` longtext,
  `razon_social` varchar(150) DEFAULT NULL,
  `nit` varchar(20) DEFAULT NULL,
  `representante_legal` varchar(150) DEFAULT NULL,
  `regimen_tributario` varchar(30) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `ciudad` varchar(100) NOT NULL,
  `departamento` varchar(100) NOT NULL,
  `telefono` varchar(30) NOT NULL,
  `correo` varchar(254) NOT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `imagen_portada` varchar(100) DEFAULT NULL,
  `creado_en` datetime(6) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_establecimiento`),
  UNIQUE KEY `nombre` (`nombre`),
  UNIQUE KEY `slug` (`slug`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `nit` (`nit`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `establecimiento`
--

LOCK TABLES `establecimiento` WRITE;
/*!40000 ALTER TABLE `establecimiento` DISABLE KEYS */;
INSERT INTO `establecimiento` VALUES (1,'Glamour & Style Salon','glamour-style-salon','eergthujtfsdsjtghfcxvcxcdjlñaskdjeiwdmlalahdhwi','Glamour & Style S.A.S.','901234567-8','Admin Glamour','NO_RESPONSABLE_IVA','Carrera 3 # 24-15, Centro','Quibdó','Chocó','3101234567','ontacto@glamourstyle.com','establecimientos/logos/Captura_de_pantalla_2025-10-03_170741.png','establecimientos/portadas/Captura_de_pantalla_2025-10-03_170741.png','2026-09-24 22:11:28.859878',1);
/*!40000 ALTER TABLE `establecimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `factura`
--

DROP TABLE IF EXISTS `factura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factura` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `nombre_establecimiento` varchar(150) DEFAULT NULL,
  `numero_factura` varchar(50) NOT NULL,
  `tipo_facturacion` varchar(20) NOT NULL,
  `cufe_cude` varchar(255) DEFAULT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `total_impuestos` decimal(12,2) NOT NULL,
  `total_general` decimal(12,2) NOT NULL,
  `metodo_pago` varchar(20) NOT NULL,
  `estado_pago` varchar(20) NOT NULL,
  `pagada` tinyint(1) NOT NULL,
  `fecha_emision` datetime(6) NOT NULL,
  `id_cita` int NOT NULL,
  PRIMARY KEY (`id_factura`),
  UNIQUE KEY `numero_factura` (`numero_factura`),
  UNIQUE KEY `id_cita` (`id_cita`),
  CONSTRAINT `factura_id_cita_ee42b3f7_fk_cita_id_cita` FOREIGN KEY (`id_cita`) REFERENCES `cita` (`id_cita`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factura`
--

LOCK TABLES `factura` WRITE;
/*!40000 ALTER TABLE `factura` DISABLE KEYS */;
INSERT INTO `factura` VALUES (1,'Glamour & Style Salon','FAC-9478F68D','FISICA',NULL,60000.00,0.00,60000.00,'EFECTIVO','PAGADO',0,'2026-09-24 23:14:28.573301',1);
/*!40000 ALTER TABLE `factura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `factura_detalle`
--

DROP TABLE IF EXISTS `factura_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factura_detalle` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `descripcion_item` varchar(200) NOT NULL,
  `cantidad` int NOT NULL,
  `valor_unitario` decimal(12,2) NOT NULL,
  `porcentaje_impuesto` decimal(5,2) NOT NULL,
  `subtotal_item` decimal(12,2) NOT NULL,
  `fecha_cita_realizada` date DEFAULT NULL,
  `hora_cita_realizada` time(6) DEFAULT NULL,
  `id_factura` int NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `factura_detalle_id_factura_289f7c5b_fk_factura_id_factura` (`id_factura`),
  CONSTRAINT `factura_detalle_id_factura_289f7c5b_fk_factura_id_factura` FOREIGN KEY (`id_factura`) REFERENCES `factura` (`id_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factura_detalle`
--

LOCK TABLES `factura_detalle` WRITE;
/*!40000 ALTER TABLE `factura_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `factura_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `horario_establecimiento`
--

DROP TABLE IF EXISTS `horario_establecimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `horario_establecimiento` (
  `id_horario` int NOT NULL AUTO_INCREMENT,
  `dia_semana` int NOT NULL,
  `hora_apertura` time(6) DEFAULT NULL,
  `hora_cierre` time(6) DEFAULT NULL,
  `cerrado` tinyint(1) NOT NULL,
  `id_establecimiento` int NOT NULL,
  PRIMARY KEY (`id_horario`),
  UNIQUE KEY `horario_establecimiento_id_establecimiento_dia_s_aadafa67_uniq` (`id_establecimiento`,`dia_semana`),
  CONSTRAINT `horario_establecimie_id_establecimiento_f653f7be_fk_estableci` FOREIGN KEY (`id_establecimiento`) REFERENCES `establecimiento` (`id_establecimiento`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `horario_establecimiento`
--

LOCK TABLES `horario_establecimiento` WRITE;
/*!40000 ALTER TABLE `horario_establecimiento` DISABLE KEYS */;
INSERT INTO `horario_establecimiento` VALUES (1,1,'08:00:00.000000','19:00:00.000000',0,1),(2,2,'08:00:00.000000','19:00:00.000000',0,1),(3,3,'08:00:00.000000','19:00:00.000000',0,1),(4,4,'08:00:00.000000','19:00:00.000000',0,1),(5,5,'08:00:00.000000','19:00:00.000000',0,1),(6,6,'08:00:00.000000','19:00:00.000000',0,1),(7,7,'09:00:00.000000','14:00:00.000000',0,1);
/*!40000 ALTER TABLE `horario_establecimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `horario_trabajador`
--

DROP TABLE IF EXISTS `horario_trabajador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `horario_trabajador` (
  `id_horario_trabajador` int NOT NULL AUTO_INCREMENT,
  `dia_semana` int NOT NULL,
  `hora_entrada` time(6) NOT NULL,
  `hora_salida` time(6) NOT NULL,
  `descanso_inicio` time(6) DEFAULT NULL,
  `descanso_fin` time(6) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `id_perfil` int NOT NULL,
  PRIMARY KEY (`id_horario_trabajador`),
  KEY `horario_trabajador_id_perfil_eb640765_fk_perfil_us` (`id_perfil`),
  CONSTRAINT `horario_trabajador_id_perfil_eb640765_fk_perfil_us` FOREIGN KEY (`id_perfil`) REFERENCES `perfil_usuario` (`id_perfil`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `horario_trabajador`
--

LOCK TABLES `horario_trabajador` WRITE;
/*!40000 ALTER TABLE `horario_trabajador` DISABLE KEYS */;
INSERT INTO `horario_trabajador` VALUES (1,1,'08:00:00.000000','17:00:00.000000','12:00:00.000000','13:00:00.000000',1,2),(2,2,'08:00:00.000000','17:00:00.000000','12:00:00.000000','13:00:00.000000',1,2),(3,3,'08:00:00.000000','17:00:00.000000','12:00:00.000000','13:00:00.000000',1,2),(4,4,'08:00:00.000000','17:00:00.000000','12:00:00.000000','13:00:00.000000',1,2),(5,5,'08:00:00.000000','17:00:00.000000','12:00:00.000000','13:00:00.000000',1,2),(6,6,'08:00:00.000000','17:00:00.000000','12:00:00.000000','13:00:00.000000',1,2),(7,7,'09:00:00.000000','12:00:00.000000',NULL,NULL,1,2);
/*!40000 ALTER TABLE `horario_trabajador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfil_usuario`
--

DROP TABLE IF EXISTS `perfil_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfil_usuario` (
  `id_perfil` int NOT NULL AUTO_INCREMENT,
  `nombre_establecimiento` varchar(150) DEFAULT NULL,
  `rol` varchar(20) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `porcentaje_comision` decimal(5,2) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `estado` tinyint(1) NOT NULL,
  `id_establecimiento` int NOT NULL,
  `id_usuario` int NOT NULL,
  PRIMARY KEY (`id_perfil`),
  UNIQUE KEY `id_usuario` (`id_usuario`),
  KEY `perfil_usuario_id_establecimiento_130e9f5f_fk_estableci` (`id_establecimiento`),
  CONSTRAINT `perfil_usuario_id_establecimiento_130e9f5f_fk_estableci` FOREIGN KEY (`id_establecimiento`) REFERENCES `establecimiento` (`id_establecimiento`),
  CONSTRAINT `perfil_usuario_id_usuario_13045d7f_fk_auth_user_id` FOREIGN KEY (`id_usuario`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfil_usuario`
--

LOCK TABLES `perfil_usuario` WRITE;
/*!40000 ALTER TABLE `perfil_usuario` DISABLE KEYS */;
INSERT INTO `perfil_usuario` VALUES (1,'Glamour & Style Salon','ADMIN_NEGOCIO','3101234567',0.00,'trabajadores/Captura_de_pantalla_2026-05-04_131740.png',1,1,2),(2,'Glamour & Style Salon','TRABAJADOR','3101234568',40.00,'trabajadores/Captura_de_pantalla_2026-05-04_131740_HifqHwy.png',1,1,3),(3,'Glamour & Style Salon','TRABAJADOR','3101234565',50.00,'trabajadores/Captura_de_pantalla_2026-05-04_131740_l3yWMvx.png',1,1,4);
/*!40000 ALTER TABLE `perfil_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resena`
--

DROP TABLE IF EXISTS `resena`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resena` (
  `id_resena` int NOT NULL AUTO_INCREMENT,
  `nombre_establecimiento` varchar(150) DEFAULT NULL,
  `calificacion` int NOT NULL,
  `comentario` longtext,
  `fecha` datetime(6) NOT NULL,
  `id_cita` int NOT NULL,
  PRIMARY KEY (`id_resena`),
  UNIQUE KEY `id_cita` (`id_cita`),
  CONSTRAINT `resena_id_cita_9d174679_fk_cita_id_cita` FOREIGN KEY (`id_cita`) REFERENCES `cita` (`id_cita`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resena`
--

LOCK TABLES `resena` WRITE;
/*!40000 ALTER TABLE `resena` DISABLE KEYS */;
/*!40000 ALTER TABLE `resena` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicio`
--

DROP TABLE IF EXISTS `servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre_establecimiento` varchar(150) DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` longtext,
  `precio` decimal(10,2) NOT NULL,
  `duracion_minutos` int NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `estado` tinyint(1) NOT NULL,
  `id_categoria` int NOT NULL,
  PRIMARY KEY (`id_servicio`),
  KEY `servicio_id_categoria_807a0d85_fk_categoria_id_categoria` (`id_categoria`),
  CONSTRAINT `servicio_id_categoria_807a0d85_fk_categoria_id_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicio`
--

LOCK TABLES `servicio` WRITE;
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
INSERT INTO `servicio` VALUES (1,'Glamour & Style Salon','Corte y Cepillado Dama','Incluye lavado con champú hidratante, corte de puntas y moldeado con secador.',45000.00,45,'servicios/Captura_de_pantalla_2026-05-04_171455.png',1,1),(2,'Glamour & Style Salon','Uñitas Semipermanentes','Limpieza de cutícula, limado, diseño básico y esmaltado de larga duración.',60000.00,60,'servicios/Captura_de_pantalla_2026-05-04_163022.png',1,2),(3,'Glamour & Style Salon','Corte Caballero y Barba','Corte moderno con degradado y perfilado de barba con toalla caliente.',30000.00,40,'servicios/Captura_de_pantalla_2026-05-05_152337.png',1,1);
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicio_trabajadoresf`
--

DROP TABLE IF EXISTS `servicio_trabajadoresf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio_trabajadoresf` (
  `id` int NOT NULL AUTO_INCREMENT,
  `servicio_id` int NOT NULL,
  `perfilusuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `servicio_trabajadoresf_servicio_id_perfilusuari_10f931db_uniq` (`servicio_id`,`perfilusuario_id`),
  KEY `servicio_trabajadore_perfilusuario_id_a8d248e8_fk_perfil_us` (`perfilusuario_id`),
  CONSTRAINT `servicio_trabajadore_perfilusuario_id_a8d248e8_fk_perfil_us` FOREIGN KEY (`perfilusuario_id`) REFERENCES `perfil_usuario` (`id_perfil`),
  CONSTRAINT `servicio_trabajadore_servicio_id_f4e244cc_fk_servicio_` FOREIGN KEY (`servicio_id`) REFERENCES `servicio` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicio_trabajadoresf`
--

LOCK TABLES `servicio_trabajadoresf` WRITE;
/*!40000 ALTER TABLE `servicio_trabajadoresf` DISABLE KEYS */;
INSERT INTO `servicio_trabajadoresf` VALUES (1,1,2),(2,2,2),(3,3,3);
/*!40000 ALTER TABLE `servicio_trabajadoresf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_auth_user` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-24 18:16:25
