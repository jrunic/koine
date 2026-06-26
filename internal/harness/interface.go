package harness

// MarkerKoine é a primeira linha de todo arquivo Markdown gerado pelo kn-agente
// em ArquivosNoWorkingDir. Permite que verificarConflitos distinga arquivos Koine
// de arquivos do usuário: presença do marker → regeneração idempotente; ausência → conflito.
const MarkerKoine = "<!-- gerado por kn-agente -->"

// Lancamento descreve tudo que o adapter quer materializar no filesystem
// e no ambiente do processo filho.
//
// Adapters simples (Claude, Antigravity) preenchem apenas ArquivosNoWorkingDir.
// Adapters com bundle externo (Copilot, OpenCode) preenchem ArquivosExternos,
// EnvVars e Symlinks.
type Lancamento struct {
	// ArquivosNoWorkingDir: path relativo a pastaAbs → conteúdo.
	// Wrapper cria diretórios pai e escreve os bytes.
	ArquivosNoWorkingDir map[string][]byte
	// ArquivosExternos: path absoluto → conteúdo.
	// Wrapper cria diretórios pai e escreve os bytes.
	ArquivosExternos map[string][]byte
	// Symlinks: path-do-symlink (absoluto) → alvo.
	// Wrapper chama os.Symlink para cada entrada.
	Symlinks map[string]string
	// EnvVars: nome → valor. Adicionados ao os.Environ() antes do syscall.Exec.
	EnvVars map[string]string
	// ExtraArgs: args adicionais concatenados na invocação do cliente IA.
	ExtraArgs []string
}

// ContextoMontado contém todos os dados resolvidos para gerar o arquivo de contexto do harness.
//
// O framework de cada domínio NÃO aparece aqui como path separado — é embutido
// no header do respectivo kn-indice-<dom>.md pelo gerador (internal/indice).
// Cada IndicePath carrega framework + catálogo de entradas em único arquivo.
//
// Bootstrap=true indica modo de pasta sem CONTEXTO.md: apenas UsuarioPath, KoineMDPath e
// AgentePath são preenchidos; EscopoPath, IndicePaths e ContextoPath ficam vazios.
// Adapters de harness devem usar template reduzido nesse caso.
type ContextoMontado struct {
	Bootstrap    bool     // true quando pasta não tem CONTEXTO.md; adapters usam template de bootstrap
	UsuarioPath  string   // ConfigDir()/<nome>.md (persona do mentee)
	KoineMDPath  string   // VaultDir()/KOINE.md
	AgentePath   string   // VaultDir()/agentes/<agente>.md ou ConfigDir()/agentes/<agente>.md
	EscopoPath   string   // ConfigDir()/escopos/<slug-escopo>.md
	IndicePaths  []string // <pasta-referencias>/kn-indice-<dom>.md, na ordem de CONTEXTO.md
	ContextoPath string   // <pasta>/CONTEXTO.md
}

// Harness abstrai o cliente IA alvo (Claude Code, Antigravity, Copilot CLI, etc.).
type Harness interface {
	Nome() string
	CaminhoArquivoContexto(cwd string) string
	Renderizar(dados ContextoMontado) (Lancamento, error)
}
