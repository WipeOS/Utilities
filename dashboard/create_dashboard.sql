drop database if exists dashboard;
create database dashboard;
use dashboard;

create table version (
   version_id int not null auto_increment,
   version_string varchar(16) not null,
   primary key (version_id)
);

create table wipebox (
    wipebox_id int not null auto_increment,
    cert int not null,
    version_id int not null,
    last_update timestamp not null default '2025-04-01 00:00:00',
    primary key(wipebox_id),
    foreign key (version_id) references version(version_id)
);

create table mount_point (
   mount_point_id int not null auto_increment,
   mount_point varchar(128) not null,
   primary key (mount_point_id)
);

create table disk_usage (
   disk_usage_id int not null auto_increment,
   mount_point_id int not null,
   wipebox_id int not null,
   total int not null,
   used int not null,
   available int not null,
   percent_used int not null,
   primary key(disk_usage_id),
   foreign key (mount_point_id) references mount_point(mount_point_id),
   foreign key (wipebox_id) references wipebox(wipebox_id)
);

create table repository (
   repository_id int not null auto_increment,
   repo_name varchar(64) not null,
   remote_url varchar(128) not null,
   primary key (repository_id)
);

create table repo_version (
   repository_id int not null,
   version_id int not null,
   hash varchar(16) not null,
   foreign key (repository_id) references repository(repository_id),
   foreign key (version_id) references version(version_id)
);

create table generic_config (
   configuration_id int not null auto_increment,
   wipebox_id int not null,
   name varchar(128) not null,
   value json not null,
   primary key (configuration_id),
   foreign key (wipebox_id) references wipebox(wipebox_id)
);

insert into repository (repo_name, remote_url) values ('ApplianceUId', 'github.com:WipeOS/ApplianceUId.git');
insert into repository (repo_name, remote_url) values ('Client-Browser', 'github.com:WipeOS/Client-Browser.git');
insert into repository (repo_name, remote_url) values ('ComputerD', 'github.com:WipeOS/ComputerD.git');
insert into repository (repo_name, remote_url) values ('WipeD', 'github.com:WipeOS/WipeD.git');
insert into repository (repo_name, remote_url) values ('Hardware-Tester', 'github.com:WipeOS/Hardware-Tester.git');
insert into repository (repo_name, remote_url) values ('ImageD', 'github.com:WipeOS/ImageD.git');
insert into repository (repo_name, remote_url) values ('autoupdate', 'github.com:WipeOS/autoupdate.git');
insert into repository (repo_name, remote_url) values ('MobileD', 'github.com:WipeOS/MobileD.git');
insert into repository (repo_name, remote_url) values ('VerifyD', 'github.com:WipeOS/VerifyD.git');
insert into repository (repo_name, remote_url) values ('WipeDB-API', 'github.com:WipeOS/WipeDB-API.git');
insert into repository (repo_name, remote_url) values ('Parsers', 'github.com:WipeOS/Parsers.git');
insert into repository (repo_name, remote_url) values ('WipeUId', 'github.com:WipeOS/WipeUId.git');
insert into repository (repo_name, remote_url) values ('WipeOS-Bottle', 'github.com:WipeOS/WipeOS-Bottle.git');

insert into mount_point (mount_point) values ('/');
insert into mount_point (mount_point) values ('/var/volatile/log');
insert into mount_point (mount_point) values ('/var/volatile/tmp');
insert into mount_point (mount_point) values ('/var/lib/postgresql');
insert into mount_point (mount_point) values ('/var/lib/postgresql/images');

insert into version (version_string) values ('2.4.18-DEV');

-- select wipebox_id,concat("<table><tr><th>Mount Point</th><th>Size</th><th>Percent Used</th></td>",group_concat(tble order by wipebox_id separator ''),"</table>") from (select wipebox_id,concat("<tr><td>",mount_point,"</td><td>",total,"G</td><td>(",percent_used,"%)</td></tr>") as tble from disk_usage du join mount_point mp on du.mount_point_id=mp.mount_point_id order by wipebox_id) t group by wipebox_id;
