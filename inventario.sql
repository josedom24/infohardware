SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `inventario` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `inventario` ;

-- -----------------------------------------------------
-- Table `inventario`.`cpu`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `inventario`.`cpu` (
  `idcpu` INT NOT NULL AUTO_INCREMENT ,
  `vendor` VARCHAR(45) NULL ,
  `product` VARCHAR(70) NULL ,
  `slot` VARCHAR(45) NULL ,
  PRIMARY KEY (`idcpu`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `inventario`.`equipo`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `inventario`.`equipo` (
  `num_serie` VARCHAR(45) NOT NULL ,
  `vendor` VARCHAR(45) NULL ,
  `product` VARCHAR(70) NULL ,
  `cpu_idcpu` INT NOT NULL ,
  PRIMARY KEY (`num_serie`) ,
  INDEX `fk_cpu_cpu1` (`cpu_idcpu` ASC) ,
  CONSTRAINT `fk_cpu_cpu1`
    FOREIGN KEY (`cpu_idcpu` )
    REFERENCES `inventario`.`cpu` (`idcpu` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `inventario`.`ram`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `inventario`.`ram` (
  `idram` INT NOT NULL AUTO_INCREMENT ,
  `size` VARCHAR(45) NULL ,
  `clock` VARCHAR(45) NULL ,
  `equipo_num_serie` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`idram`) ,
  INDEX `fk_ram_equipo1` (`equipo_num_serie` ASC) ,
  CONSTRAINT `fk_ram_equipo1`
    FOREIGN KEY (`equipo_num_serie` )
    REFERENCES `inventario`.`equipo` (`num_serie` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `inventario`.`hd`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `inventario`.`hd` (
  `serial` VARCHAR(45) NOT NULL ,
  `equipo_num_serie` VARCHAR(45) NOT NULL ,
  `vendor` VARCHAR(45) NULL ,
  `product` VARCHAR(70) NULL ,
  `description` VARCHAR(45) NULL ,
  `size` VARCHAR(45) NULL ,
  PRIMARY KEY (`serial`, `equipo_num_serie`) ,
  INDEX `fk_hd_equipo1` (`equipo_num_serie` ASC) ,
  CONSTRAINT `fk_hd_equipo1`
    FOREIGN KEY (`equipo_num_serie` )
    REFERENCES `inventario`.`equipo` (`num_serie` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `inventario`.`cd`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `inventario`.`cd` (
  `idcd` INT NOT NULL AUTO_INCREMENT ,
  `vendor` VARCHAR(45) NULL ,
  `product` VARCHAR(70) NULL ,
  `equipo_num_serie` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`idcd`) ,
  INDEX `fk_cd_equipo1` (`equipo_num_serie` ASC) ,
  CONSTRAINT `fk_cd_equipo1`
    FOREIGN KEY (`equipo_num_serie` )
    REFERENCES `inventario`.`equipo` (`num_serie` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `inventario`.`red`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `inventario`.`red` (
  `mac` VARCHAR(45) NOT NULL ,
  `equipo_num_serie` VARCHAR(45) NOT NULL ,
  `vendor` VARCHAR(45) NULL ,
  `product` VARCHAR(70) NULL ,
  PRIMARY KEY (`mac`, `equipo_num_serie`) ,
  INDEX `fk_red_equipo1` (`equipo_num_serie` ASC) ,
  CONSTRAINT `fk_red_equipo1`
    FOREIGN KEY (`equipo_num_serie` )
    REFERENCES `inventario`.`equipo` (`num_serie` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
