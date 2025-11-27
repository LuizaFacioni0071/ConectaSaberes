document.addEventListener('DOMContentLoaded', function() {
    
    /* ============================================================
       1. MÁSCARA PARA WHATSAPP
       Objetivo: Garantir que o usuário digite apenas números.
       O link wa.me precisa de números limpos (sem parênteses ou traços).
    ============================================================ */
    const whatsappInput = document.getElementById('whatsapp');

    if (whatsappInput) {
        whatsappInput.addEventListener('input', function(e) {
            // Remove qualquer caractere que NÃO seja número
            let valorLimpo = e.target.value.replace(/\D/g, '');
            
            // Limita a 11 dígitos (DDD + 9 + 8 números) - Padrão BR
            if (valorLimpo.length > 11) {
                valorLimpo = valorLimpo.slice(0, 11);
            }

            e.target.value = valorLimpo;
        });
    }

    /* ============================================================
       2. SUMIR ALERTAS AUTOMATICAMENTE (Flash Messages)
       Objetivo: Melhorar a interface limpando mensagens antigas.
    ============================================================ */
    const alertas = document.querySelectorAll('.alert');

    if (alertas.length > 0) {
        // Espera 5 segundos (5000ms) e então começa a sumir
        setTimeout(function() {
            alertas.forEach(function(alerta) {
                // Adiciona um efeito de transição suave via CSS inline
                alerta.style.transition = "opacity 0.5s ease";
                alerta.style.opacity = "0";

                // Depois que ficar transparente, remove do HTML
                setTimeout(function() {
                    alerta.remove();
                }, 500); 
            });
        }, 5000);
    }
});

/* ============================================================
   3. FUNÇÕES DE ACESSIBILIDADE (Escopo Global)
   Objetivo: Permitir controle de fonte e contraste.
   São chamadas pelos botões onclick="..." no HTML.
============================================================ */

// Variável para rastrear o tamanho atual da fonte
let tamanhoFonteAtual = 16; // 16px é o padrão da maioria dos navegadores

function mudarFonte(valor) {
    // Aumenta ou diminui o valor
    tamanhoFonteAtual += valor;

    // Define limites para não quebrar o layout (Min 12px, Max 24px)
    if (tamanhoFonteAtual > 24) tamanhoFonteAtual = 24;
    if (tamanhoFonteAtual < 12) tamanhoFonteAtual = 12;

    // Aplica o novo tamanho ao corpo do site
    document.body.style.fontSize = tamanhoFonteAtual + "px";
}

function alternarContraste() {
    // Adiciona ou remove a classe 'alto-contraste' no body
    // O CSS se encarrega de mudar as cores quando essa classe existe
    document.body.classList.toggle('alto-contraste');
}

/* ============================================================
   4. REGISTRO DE MÉTRICAS (Fetch API)
   Objetivo: Salvar no banco quando um aluno clica no WhatsApp.
============================================================ */
function registrarConexao(mentorId) {
    // Faz uma chamada silenciosa (AJAX) para o backend
    fetch(`/registrar_conexao/${mentorId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Sucesso:', data.mensagem);
        })
        .catch(error => {
            console.error('Erro ao registrar métrica:', error);
        });
        
    // Nota: O link do WhatsApp continuará abrindo normalmente na nova aba
}
