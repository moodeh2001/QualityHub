-- DB-TC-010: email uniqueness within each sandbox, not globally.
SELECT sandbox_id, lower(email) AS normalized_email, count(*)
FROM public.users GROUP BY sandbox_id, lower(email) HAVING count(*) > 1;
