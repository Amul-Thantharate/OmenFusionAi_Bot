CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_subscribed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    message TEXT,
    response TEXT,
    model VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS image_generations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    prompt TEXT,
    enhanced_prompt TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS image_captions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    image_url TEXT,
    caption TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS text_enhancements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    original_text TEXT,
    enhanced_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS image_descriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    image_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS video_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    video_url TEXT,
    analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
); 