package config

// ExportLookupConfigDir e SetLookupConfigDir são acessores para injeção cruzada
// de pacotes em testes (ver internal/contexto/leitor_test.go).
//
// NÃO USE EM PRODUÇÃO. A única razão de serem exportados é que arquivos *_test.go
// não cruzam fronteira de pacote no Go — outro pacote que importa `config` em
// teste não enxerga símbolos de `hooks_test.go`. Padrão equivalente ao usado por
// stdlib quando precisa expor hooks privados a testes de pacotes vizinhos.
func ExportLookupConfigDir() func() string { return lookupConfigDir }
func SetLookupConfigDir(f func() string)   { lookupConfigDir = f }
