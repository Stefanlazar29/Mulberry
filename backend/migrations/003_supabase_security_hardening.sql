-- Supabase Security Hardening
-- Rulează în Supabase Dashboard → SQL Editor

-- 1. Fix search_path mutable pe handle_new_user
--    Previne search_path injection attacks
ALTER FUNCTION public.handle_new_user()
  SET search_path = public, pg_catalog;

-- 2. Revocă execute public pe SECURITY DEFINER function
--    Funcția rulează doar prin trigger la auth.users INSERT, nu direct
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM authenticated;

-- Verificare: funcția trebuie să fie apelabilă DOAR de postgres/service_role
-- (triggerul rulează cu drepturile owner-ului, nu ale caller-ului)
