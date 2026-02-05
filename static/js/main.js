document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn-satisfacao');
    const feedback = document.getElementById('feedback');
    let isBlocked = false;
    const TIMEOUT_DURATION = 3000;

    buttons.forEach(button => {
        button.addEventListener('click', async function() {
            if (isBlocked) return;

            const grau = this.dataset.grau;
            
            buttons.forEach(btn => btn.disabled = true);
            isBlocked = true;

            try {
                const response = await fetch('/registar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ grau: grau })
                });

                const data = await response.json();

                if (data.success) {
                    showFeedback();
                }
            } catch (error) {
                console.error('Erro ao registar avaliação:', error);
            }

            setTimeout(() => {
                buttons.forEach(btn => btn.disabled = false);
                isBlocked = false;
            }, TIMEOUT_DURATION);
        });
    });

    function showFeedback() {
        feedback.classList.add('show');
        
        setTimeout(() => {
            feedback.classList.remove('show');
        }, 2000);
    }
});
