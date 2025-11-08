CREATE TABLE `generated_contents` (
	`id` int AUTO_INCREMENT NOT NULL,
	`region_name` varchar(100) NOT NULL,
	`theme_name` varchar(100) NOT NULL,
	`hotel_no` int,
	`hotel_name` varchar(200),
	`template_id` varchar(10) NOT NULL,
	`template_name` varchar(100) NOT NULL,
	`content` text NOT NULL,
	`word_count` int NOT NULL,
	`generated_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `generated_contents_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `hotels` (
	`id` int AUTO_INCREMENT NOT NULL,
	`hotel_no` int NOT NULL,
	`hotel_name` varchar(200) NOT NULL,
	`hotel_image_url` varchar(500),
	`hotel_min_charge` int,
	`address1` varchar(100),
	`address2` varchar(200),
	`access` text,
	`hotel_information_url` varchar(500),
	`review_average` int,
	`review_count` int,
	`hotel_special` text,
	`region_name` varchar(100) NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT (now()),
	`updated_at` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `hotels_id` PRIMARY KEY(`id`),
	CONSTRAINT `hotels_hotel_no_unique` UNIQUE(`hotel_no`)
);
