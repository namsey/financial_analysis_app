from flask import Flask, request, jsonify, render_template
import yfinance as yf
import pandas as pd
import logging
import openai
import os

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


def analyze_company_with_ai(company_name):
    try:
        logging.debug(f"Analyzing company: {company_name}")
        # Fetch company data
        ticker = yf.Ticker(company_name)
        info = ticker.info

        if not info:
            return {'error': f"Unable to fetch data for ticker symbol: {company_name}"}

        financials = ticker.financials

        if financials.empty:
            return {'error': f"No financial data available for ticker symbol: {company_name}"}

        # Prepare financial data for AI analysis
        financial_summary = f"""
        Company: {company_name}
        Revenue: {financials.loc['Total Revenue'].to_dict() if 'Total Revenue' in financials.index else 'N/A'}
        Net Income: {financials.loc['Net Income'].to_dict() if 'Net Income' in financials.index else 'N/A'}
        Total Assets: {info.get('totalAssets', 'N/A')}
        Total Debt: {info.get('totalDebt', 'N/A')}
        Operating Cash Flow: {info.get('operatingCashflow', 'N/A')}
        Industry: {info.get('industry', 'N/A')}
        Forward P/E: {info.get('forwardPE', 'N/A')}
        """

        # Prepare the prompt for GPT-4
        prompt = f"""
        As a financial analyst, evaluate the following financial data and provide insights:

        {financial_summary}

        Please analyze the following aspects:
        1. Revenue Trend
        2. Profitability
        3. Debt Levels
        4. Cash Flow Generation
        5. Industry Health
        6. Valuation
        7. Overall Recommendation

        Provide a concise analysis for each aspect and an overall recommendation.
        Format your response as a JSON object with the following keys:
        "revenueTrend", "profitability", "debtLevels", "cashFlow", "industryHealth", "valuation", "recommendation"
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a skilled financial analyst providing insights on company financials."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the AI's analysis
        analysis = response.choices[0].message['content']

        # Parse the JSON response
        import json
        analysis_dict = json.loads(analysis)

        # Add company name to the result
        analysis_dict['companyName'] = company_name

        return analysis_dict

    except Exception as e:
        logging.error(f"Error in analyze_company_with_ai: {str(e)}")
        return {'error': f"An error occurred while analyzing the company: {str(e)}"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    logging.debug(f"Received request: {request.json}")
    company_name = request.json['companyName']
    result = analyze_company_with_ai(company_name)
    logging.debug(f"Analysis result: {result}")
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)