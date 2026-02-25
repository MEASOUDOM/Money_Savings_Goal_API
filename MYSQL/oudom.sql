CREATE TABLE `goals` (
  `id` bigint(20) NOT NULL,
  `name` varchar(120) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `currency_id` int(11) DEFAULT NULL,
  `goal_amount` decimal(18,2) NOT NULL DEFAULT 0.00,
  `saved_amount` decimal(18,2) NOT NULL DEFAULT 0.00,
  `target_date` date DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;



CREATE TABLE `currencies` (
  `id` int(11) NOT NULL,
  `code` varchar(20) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `is_active` tinyint(4) NOT NULL COMMENT '1=active, 0=inactive'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `goal_add` (
  `id` bigint(20) NOT NULL,
  `goal_id` bigint(20) NOT NULL,
  `action` tinyint(4) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `to_goal_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;



CREATE TABLE `goal_transactions` (
  `id` bigint(20) NOT NULL,
  `goal_id` bigint(20) DEFAULT NULL,
  `type` tinyint(4) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `note` varchar(255) DEFAULT NULL,
  `txn_date` datetime DEFAULT current_timestamp(),
  `from_goal_id` bigint(20) DEFAULT NULL,
  `to_goal_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


ALTER TABLE goals
  MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ADD PRIMARY KEY (id);

ALTER TABLE goal_add
  MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ADD PRIMARY KEY (id);

ALTER TABLE goal_transactions
  MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ADD PRIMARY KEY (id);


-- API Documentation available at
-- http://127.0.0.1:8000/docs