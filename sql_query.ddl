/*
CREATE 'users'
*/
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  `hashed_password` varchar(60) COLLATE utf8mb4_bin NOT NULL,
  `salt` varchar(30) COLLATE utf8mb4_bin NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin

/*
CREATE 'account_books'
*/
CREATE TABLE `account_books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `spent_amount` bigint unsigned NOT NULL,
  `memo` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `account_books_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin

/*
CREATE 'short_urls'
*/
CREATE TABLE `short_urls` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account_book_id` int NOT NULL,
  `short_url` varchar(10) COLLATE utf8mb4_bin NOT NULL,
  `expired_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `short_url` (`short_url`),
  KEY `account_book_id` (`account_book_id`),
  CONSTRAINT `short_urls_ibfk_1` FOREIGN KEY (`account_book_id`) REFERENCES `account_books` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin


