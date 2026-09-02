CREATE TABLE IF NOT EXISTS baskets (
  id         int         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name       varchar(50) NOT NULL UNIQUE,
  token      uuid        NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  capacity   int         NOT NULL        DEFAULT 200 CHECK (capacity > 0 AND capacity <= 400),
  expires_at timestamptz NOT NULL        DEFAULT NOW() + INTERVAL '72 hours',

  CONSTRAINT alphanumeric_name_only CHECK(name ~ '^[A-Za-z0-9]+$' ),
  CONSTRAINT baskets_name_reserved  CHECK(lower(name) <> 'baskets')
);

CREATE INDEX IF NOT EXISTS baskets_name_index ON baskets(name);

DO $$
BEGIN
  CREATE TYPE http_method AS ENUM (
    'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD',
    'CONNECT', 'OPTIONS', 'TRACE'
  );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

CREATE TABLE IF NOT EXISTS requests (
  id           uuid         PRIMARY KEY,
  basket_id    int          NOT NULL REFERENCES baskets ON DELETE CASCADE,
  method       http_method  NOT NULL,
  path         varchar(255) NOT NULL,
  headers      jsonb        NOT NULL DEFAULT jsonb_build_object(), -- Headers are case-insensitive; normalize case in application code!
  query_params jsonb        NOT NULL DEFAULT jsonb_build_object(),
  body         text,
  received_at  timestamptz  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS requests_basket_id_index ON requests (basket_id);
