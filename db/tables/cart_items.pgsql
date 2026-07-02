CREATE TABLE cart_items (
    id          SERIAL PRIMARY KEY,
    created_at  INT NOT NULL,
    updated_at  INT NOT NULL,
    user_id     INT NOT NULL REFERENCES users(id),
    item_id     INT NOT NULL REFERENCES items(id),
    amount      SMALLINT NOT NULL
);

CREATE INDEX idx_cart_items_user_id ON cart_items (user_id);