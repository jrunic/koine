package contexto

// ExportLookupVaultDir e SetLookupVaultDir são acessores para injeção cruzada
// de pacotes em testes (ver cmd/kn-agente/wrapper_test.go).
// NÃO USE EM PRODUÇÃO. Mesmo padrão de internal/config/hooks.go.
func ExportLookupVaultDir() func() string { return lookupVaultDir }
func SetLookupVaultDir(f func() string)   { lookupVaultDir = f }
