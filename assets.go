package koine

import "embed"

// VaultFS contém o vault embutido no binário via go:embed.
// Acessado em runtime por internal/instalar e internal/render.
//
//go:embed vault
var VaultFS embed.FS
