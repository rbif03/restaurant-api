CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    created_at  INT NOT NULL,
    updated_at  INT NOT NULL,
    user_id     INT NOT NULL REFERENCES users(id),
    status order_status NOT NULL  -- enum type
);

CREATE INDEX idx_orders_user_id ON orders (user_id);