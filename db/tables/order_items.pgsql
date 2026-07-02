CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    created_at  INT NOT NULL,
    updated_at  INT NOT NULL,
    order_id     INT NOT NULL REFERENCES orders(id),
    item_id INT NOT NULL REFERENCES items(id),
    amount SMALLINT NOT NULL
);

CREATE INDEX idx_order_items_order_id ON order_items (order_id);