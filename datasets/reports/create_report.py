import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader
import os

class CannabisReport:

    def __init__(self, data_paths):
        self.data_paths = data_paths
        self.data = self.load_data()
        self.clean_data()

    def load_data(self):
        # Concatenate data from all paths.
        data = pd.concat((pd.read_csv(path) for path in self.data_paths))
        return data

    def clean_data(self):
        # Perform necessary data cleaning.
        # Remove NA values for now, you may want to fill them appropriately based on your specific needs
        self.data = self.data.dropna()

    def analyze(self):
        # Perform necessary data analysis.
        results = {}

        # Example: Count of lab results by state
        results['count_by_state'] = self.data['distributor_state'].value_counts().to_dict()

        # Example: Average Total Cannabinoids by state
        results['avg_total_cannabinoids_by_state'] = self.data.groupby('distributor_state')['total_cannabinoids'].mean().to_dict()

        # Example: Maximum Total Cannabinoids by state
        results['max_total_cannabinoids_by_state'] = self.data.groupby('distributor_state')['total_cannabinoids'].max().to_dict()

        # Save DataFrame as LaTeX table
        df = self.data.groupby('distributor_state')['total_cannabinoids'].agg(['mean', 'max'])
        with open('table.tex', 'w') as f:
            f.write(df.to_latex())

        return results
    
    def analyze_time_series(self):
        # Analyze time series data.
        # Convert date columns to datetime.
        for col in ['date_collected', 'date_tested', 'date_received']:
            self.data[col] = pd.to_datetime(self.data[col])
            
        # Count number of tests performed each month
        self.data['month_year_tested'] = self.data['date_tested'].dt.to_period('M')
        tests_per_month = self.data['month_year_tested'].value_counts().sort_index().to_dict()

        return tests_per_month
    
    def analyze_variables(self):
        # Analyze specific variables
        variables = ['total_cannabinoids', 'total_thc', 'total_cbd', 'total_terpenes']
        stats = {}
        
        for var in variables:
            stats[var] = {
                'mean': self.data[var].mean(),
                'median': self.data[var].median(),
                'std_dev': self.data[var].std(),
            }
            
        return stats
    
    def analyze_strains(self):
        # Analyze the popularity of strains
        top_strains = self.data['strain_name'].value_counts().head(10).to_dict()
        return top_strains

    def analyze_sales(self):
        # Analyze the amount being sold by retailers
        # This assumes a 'sales' column in your data, replace with the correct column name if different
        top_retailers = self.data.groupby('distributor')['sales'].sum().sort_values(ascending=False).head(10).to_dict()
        return top_retailers
    
    def analyze_product_types(self):
        # Analyze the distribution of product types
        product_types = self.data['product_type'].value_counts().to_dict()
        return product_types

    def analyze_pass_rates(self):
        # Analyze the pass rates for labs
        pass_rates = self.data.groupby('lab_id')['status'].apply(lambda x: (x == 'pass').mean()).to_dict()
        return pass_rates

    def analyze_sales_over_time(self):
        # Analyze total sales over time
        # This assumes a 'sales' column in your data, replace with the correct column name if different
        self.data['month_year'] = self.data['date_tested'].dt.to_period('M')
        sales_over_time = self.data.groupby('month_year')['sales'].sum().to_dict()
        return sales_over_time
    
    def analyze_fun_stats(self):
        # Fun Stat #1: The day with the most testing
        most_common_test_day = self.data['date_tested'].dt.day_name().value_counts().idxmax()
        
        # Fun Stat #2: The most common collection time of the day
        most_common_collection_hour = self.data['date_collected'].dt.hour.value_counts().idxmax()
        
        # Fun Stat #3: The strain with the highest average total THC
        highest_thc_strain = self.data.groupby('strain_name')['total_thc'].mean().idxmax()

        # Fun Stat #4: The strain with the highest average total CBD
        highest_cbd_strain = self.data.groupby('strain_name')['total_cbd'].mean().idxmax()

        # And so on...

        fun_stats = {
            'most_common_test_day': most_common_test_day,
            'most_common_collection_hour': most_common_collection_hour,
            'highest_thc_strain': highest_thc_strain,
            'highest_cbd_strain': highest_cbd_strain,
            # And so on...
        }

        return fun_stats

    def visualize(self):
        # Perform necessary data visualizations
        visuals = {}

        # Example: Histogram of Total Cannabinoids
        plt.hist(self.data['total_cannabinoids'], bins=30, edgecolor='black')
        plt.title('Distribution of Total Cannabinoids')
        plt.xlabel('Total Cannabinoids')
        plt.ylabel('Frequency')
        plt.savefig('total_cannabinoids.png')
        visuals['total_cannabinoids'] = 'total_cannabinoids.png'

        # Example: Boxplot of Total Cannabinoids by state
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='distributor_state', y='total_cannabinoids', data=self.data)
        plt.title('Boxplot of Total Cannabinoids by State')
        plt.xlabel('State')
        plt.ylabel('Total Cannabinoids')
        plt.savefig('boxplot.png')
        visuals['boxplot'] = 'boxplot.png'

        return visuals
    
    def visualize_time_series(self, tests_per_month):
        # Visualize time series data
        plt.figure(figsize=(12, 6))
        plt.plot(list(tests_per_month.keys()), list(tests_per_month.values()), marker='o')
        plt.title('Number of Tests Performed Each Month')
        plt.xlabel('Month')
        plt.ylabel('Number of Tests')
        plt.xticks(rotation=90)
        plt.grid()
        plt.tight_layout()
        plt.savefig('tests_per_month.png')

        return 'tests_per_month.png'
    
    def visualize_distributions(self):
        # Visualize distributions of specific variables
        visuals = {}

        variables = ['total_cannabinoids', 'total_thc', 'total_cbd', 'total_terpenes']
        for var in variables:
            plt.figure(figsize=(10, 6))
            sns.histplot(self.data[var], kde=True)
            plt.title(f'Distribution of {var}')
            plt.savefig(f'{var}_dist.png')
            visuals[var] = f'{var}_dist.png'
            
        return visuals

    def visualize_correlations(self):
        # Visualize correlations between specific variables
        variables = ['total_cannabinoids', 'total_thc', 'total_cbd', 'total_terpenes']
        correlation_matrix = self.data[variables].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
        plt.title('Correlation Matrix')
        plt.savefig('correlation_matrix.png')

        return 'correlation_matrix.png'
    
    def visualize_top(self, top_dict, title, filename):
        # Visualize top items in a dictionary
        plt.figure(figsize=(10, 6))
        plt.bar(top_dict.keys(), top_dict.values())
        plt.title(title)
        plt.xticks(rotation=90)
        plt.savefig(filename)
        return filename

    def generate_report(self, results, visuals):
        # Load the Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('template.tex')

        # Render the LaTeX template
        output = template.render(results=results, visuals=visuals)

        # Write the rendered LaTeX template to a .tex file
        with open('report.tex', 'w') as file:
            file.write(output)

        # Compile the .tex file into a .pdf file using pdflatex
        os.system('pdflatex report.tex')


# === Create a report ===
if __name__ == '__main__':


    # Generate a report.
    report = CannabisReport(data_paths=['data1.csv', 'data2.csv', ...])
    results = report.analyze()
    visuals = report.visualize()

    # After creating the report object
    tests_per_month = report.analyze_time_series()
    tests_per_month_plot = report.visualize_time_series(tests_per_month)

    # Add new results and visuals to the existing dictionaries before generating the report
    results['tests_per_month'] = tests_per_month
    visuals['tests_per_month'] = tests_per_month_plot

    # After creating the report object
    variable_stats = report.analyze_variables()
    variable_dist_visuals = report.visualize_distributions()
    correlation_matrix_visual = report.visualize_correlations()

    # Add new results and visuals to the existing dictionaries before generating the report
    results['variable_stats'] = variable_stats
    visuals.update(variable_dist_visuals)
    visuals['correlation_matrix'] = correlation_matrix_visual

    # After creating the report object
    top_strains = report.analyze_strains()
    top_retailers = report.analyze_sales()
    top_strains_visual = report.visualize_top(top_strains, 'Top 10 Strains', 'top_strains.png')
    top_retailers_visual = report.visualize_top(top_retailers, 'Top 10 Retailers by Sales', 'top_retailers.png')

    # Add new results and visuals to the existing dictionaries before generating the report
    results['top_strains'] = top_strains
    results['top_retailers'] = top_retailers
    visuals['top_strains'] = top_strains_visual
    visuals['top_retailers'] = top_retailers_visual

    # After creating the report object
    product_types = report.analyze_product_types()
    pass_rates = report.analyze_pass_rates()
    sales_over_time = report.analyze_sales_over_time()

    # Add new results to the existing dictionary before generating the report
    results['product_types'] = product_types
    results['pass_rates'] = pass_rates
    results['sales_over_time'] = sales_over_time

    # Add fun statistics.
    fun_stats = report.analyze_fun_stats()
    results['fun_stats'] = fun_stats

    # Mint the report.
    report.generate_report(results, visuals)
