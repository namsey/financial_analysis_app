document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const companyName = document.getElementById('companyName').value;
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = 'Analyzing...';
    resultDiv.style.display = 'block';
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ companyName }),
        });
        const data = await response.json();
        if (data.error) {
            resultDiv.innerHTML = `<p class="error">Error: ${data.error}</p>`;
        } else {
            resultDiv.innerHTML = `
                <h2>AI Analysis Results for ${data.companyName}</h2>
                <p><strong>Revenue Trend:</strong> ${data.revenueTrend}</p>
                <p><strong>Profitability:</strong> ${data.profitability}</p>
                <p><strong>Debt Levels:</strong> ${data.debtLevels}</p>
                <p><strong>Cash Flow Generation:</strong> ${data.cashFlow}</p>
                <p><strong>Industry Health:</strong> ${data.industryHealth}</p>
                <p><strong>Valuation:</strong> ${data.valuation}</p>
                <p><strong>Recommendation:</strong> ${data.recommendation}</p>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Error occurred while analyzing. Please try again. Details: ${error.message}</p>`;
    }
});