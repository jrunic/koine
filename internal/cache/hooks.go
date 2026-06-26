package cache

// ExportLookupCacheDir e SetLookupCacheDir são acessores para injeção cruzada
// de pacotes em testes. NÃO USE EM PRODUÇÃO. Mesmo padrão de internal/config/hooks.go.
func ExportLookupCacheDir() func() string { return lookupCacheDir }
func SetLookupCacheDir(f func() string)   { lookupCacheDir = f }
