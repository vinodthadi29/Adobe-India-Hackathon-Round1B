#!/usr/bin/env python3
"""
Create sample PDF files for testing the Document Intelligence application
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_pdf(filename, content, title):
    """Create a PDF file with the given content"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)
    
    # Content
    c.setFont("Helvetica", 12)
    y_position = height - 100
    
    for line in content.split('\n'):
        if y_position < 50:  # Start new page if needed
            c.showPage()
            y_position = height - 50
        c.drawString(50, y_position, line)
        y_position -= 20
    
    c.save()

# Create test PDFs with different content types
test_pdfs = [
    {
        "filename": "/app/test_pdfs/software_engineering.pdf",
        "title": "Software Engineering Best Practices",
        "content": """
Software Engineering Best Practices

Introduction to Software Development
Software engineering is a systematic approach to the design, development, and maintenance of software systems.
It involves applying engineering principles to software development to ensure reliability, efficiency, and maintainability.

Key Principles:
1. Modularity - Breaking down complex systems into smaller, manageable components
2. Abstraction - Hiding implementation details while exposing necessary interfaces
3. Encapsulation - Bundling data and methods that operate on that data
4. Inheritance - Creating new classes based on existing ones
5. Polymorphism - Using a single interface to represent different underlying forms

Development Methodologies:
- Agile Development: Iterative and incremental approach
- Waterfall Model: Sequential design process
- DevOps: Integration of development and operations
- Test-Driven Development: Writing tests before code

Version Control Systems:
Git is the most widely used distributed version control system.
It allows multiple developers to work on the same project simultaneously.
Key Git commands include clone, add, commit, push, pull, and merge.

Code Quality:
- Write clean, readable code
- Follow coding standards and conventions
- Implement proper error handling
- Use meaningful variable and function names
- Add comprehensive documentation

Testing Strategies:
- Unit Testing: Testing individual components
- Integration Testing: Testing component interactions
- System Testing: Testing the complete system
- Acceptance Testing: Validating requirements

Software Architecture Patterns:
- Model-View-Controller (MVC)
- Microservices Architecture
- Service-Oriented Architecture (SOA)
- Event-Driven Architecture

Performance Optimization:
- Algorithm optimization
- Database query optimization
- Caching strategies
- Load balancing
- Code profiling and monitoring
        """
    },
    {
        "filename": "/app/test_pdfs/machine_learning.pdf",
        "title": "Machine Learning Fundamentals",
        "content": """
Machine Learning Fundamentals

Introduction to Machine Learning
Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience.
It focuses on developing algorithms that can automatically learn patterns from data without being explicitly programmed.

Types of Machine Learning:
1. Supervised Learning - Learning with labeled training data
2. Unsupervised Learning - Finding patterns in unlabeled data
3. Reinforcement Learning - Learning through interaction with environment

Supervised Learning Algorithms:
- Linear Regression: Predicting continuous values
- Logistic Regression: Binary and multiclass classification
- Decision Trees: Rule-based learning
- Random Forest: Ensemble of decision trees
- Support Vector Machines: Finding optimal decision boundaries
- Neural Networks: Inspired by biological neural networks

Unsupervised Learning Techniques:
- K-Means Clustering: Partitioning data into k clusters
- Hierarchical Clustering: Creating tree-like cluster structures
- Principal Component Analysis (PCA): Dimensionality reduction
- Association Rules: Finding relationships between variables

Deep Learning:
Deep learning uses neural networks with multiple hidden layers.
Popular architectures include:
- Convolutional Neural Networks (CNNs) for image processing
- Recurrent Neural Networks (RNNs) for sequential data
- Transformers for natural language processing

Model Evaluation:
- Cross-validation techniques
- Confusion matrices
- Precision, recall, and F1-score
- ROC curves and AUC
- Bias-variance tradeoff

Feature Engineering:
- Feature selection methods
- Feature scaling and normalization
- Handling missing data
- Encoding categorical variables
- Creating polynomial features

Overfitting and Regularization:
- L1 and L2 regularization
- Dropout in neural networks
- Early stopping
- Data augmentation techniques

Popular ML Libraries:
- Python: scikit-learn, TensorFlow, PyTorch, Keras
- R: caret, randomForest, e1071
- Java: Weka, MOA
- Scala: Spark MLlib
        """
    },
    {
        "filename": "/app/test_pdfs/cooking_recipes.pdf",
        "title": "Traditional Cooking Recipes",
        "content": """
Traditional Cooking Recipes

Classic Italian Pasta Carbonara
Ingredients:
- 400g spaghetti
- 200g pancetta or guanciale
- 4 large eggs
- 100g Pecorino Romano cheese, grated
- Black pepper
- Salt

Instructions:
1. Cook pasta in salted boiling water until al dente
2. Fry pancetta until crispy
3. Whisk eggs with cheese and pepper
4. Combine hot pasta with pancetta
5. Add egg mixture off heat, stirring quickly
6. Serve immediately with extra cheese

French Coq au Vin
A classic French dish of chicken braised in wine.
Ingredients:
- 1 whole chicken, cut into pieces
- 750ml red wine
- 200g bacon lardons
- 12 pearl onions
- 250g mushrooms
- 2 bay leaves
- Fresh thyme
- Butter and flour for thickening

Preparation:
1. Marinate chicken in wine overnight
2. Brown chicken pieces in a heavy pot
3. Add vegetables and herbs
4. Simmer slowly for 1.5 hours
5. Thicken sauce with butter and flour

Indian Butter Chicken
A creamy, mildly spiced curry dish.
Ingredients:
- 1kg chicken, cut into pieces
- 400ml coconut milk
- 200ml tomato puree
- Garam masala, turmeric, cumin
- Fresh ginger and garlic
- Butter and cream

Cooking Method:
1. Marinate chicken in yogurt and spices
2. Cook chicken until tender
3. Prepare sauce with tomatoes and spices
4. Combine chicken with sauce
5. Finish with cream and butter

Mexican Tacos al Pastor
Traditional Mexican street food.
Ingredients:
- Pork shoulder, thinly sliced
- Pineapple
- Corn tortillas
- White onion, diced
- Cilantro, chopped
- Lime wedges
- Salsa verde

Preparation:
1. Marinate pork in achiote paste
2. Cook on vertical spit or grill
3. Warm tortillas on griddle
4. Assemble with meat, pineapple, onion
5. Garnish with cilantro and lime

Baking Techniques:
- Proper oven temperature control
- Understanding gluten development
- Yeast activation and fermentation
- Measuring ingredients by weight
- Creating steam for crusty bread
        """
    },
    {
        "filename": "/app/test_pdfs/data_science.pdf",
        "title": "Data Science Methodology",
        "content": """
Data Science Methodology

Introduction to Data Science
Data science combines statistics, programming, and domain expertise to extract insights from data.
It involves collecting, cleaning, analyzing, and interpreting large datasets to solve business problems.

Data Science Process:
1. Problem Definition - Understanding business objectives
2. Data Collection - Gathering relevant data sources
3. Data Cleaning - Handling missing values and outliers
4. Exploratory Data Analysis - Understanding data patterns
5. Feature Engineering - Creating meaningful variables
6. Model Building - Applying statistical and ML techniques
7. Model Evaluation - Assessing performance metrics
8. Deployment - Implementing solutions in production

Statistical Foundations:
- Descriptive statistics: mean, median, mode, variance
- Probability distributions: normal, binomial, Poisson
- Hypothesis testing: t-tests, chi-square, ANOVA
- Correlation and causation analysis
- Regression analysis: linear and logistic regression

Data Visualization:
Effective visualization techniques include:
- Histograms for distribution analysis
- Scatter plots for correlation
- Box plots for outlier detection
- Heat maps for correlation matrices
- Time series plots for temporal data

Big Data Technologies:
- Apache Hadoop: Distributed storage and processing
- Apache Spark: Fast cluster computing
- NoSQL databases: MongoDB, Cassandra
- Data warehousing: Snowflake, Redshift
- Stream processing: Kafka, Storm

Python for Data Science:
Essential libraries:
- NumPy: Numerical computing
- Pandas: Data manipulation and analysis
- Matplotlib/Seaborn: Data visualization
- Scikit-learn: Machine learning
- Jupyter: Interactive development environment

SQL for Data Analysis:
- SELECT statements with filtering
- JOIN operations for combining tables
- Aggregate functions: COUNT, SUM, AVG
- Window functions for advanced analytics
- Common Table Expressions (CTEs)

A/B Testing:
- Experimental design principles
- Statistical significance testing
- Sample size calculation
- Control and treatment groups
- Interpreting results and making decisions

Data Ethics:
- Privacy and data protection
- Bias in algorithms and datasets
- Transparency in model decisions
- Responsible AI practices
- GDPR and data compliance
        """
    },
    {
        "filename": "/app/test_pdfs/biology_research.pdf",
        "title": "Molecular Biology Research Methods",
        "content": """
Molecular Biology Research Methods

DNA Extraction and Purification
DNA extraction is a fundamental technique in molecular biology research.
Common methods include:
- Phenol-chloroform extraction
- Silica column-based purification
- Magnetic bead separation
- Alkaline lysis for plasmid DNA

Quality assessment involves:
- Spectrophotometric analysis (A260/A280 ratio)
- Gel electrophoresis
- Fluorometric quantification

Polymerase Chain Reaction (PCR)
PCR amplifies specific DNA sequences exponentially.
Key components:
- Template DNA
- Primers (forward and reverse)
- DNA polymerase (Taq polymerase)
- dNTPs (deoxynucleotide triphosphates)
- Buffer and MgCl2

PCR cycling conditions:
1. Denaturation: 94-98°C
2. Annealing: 50-65°C (primer-dependent)
3. Extension: 72°C
4. Repeat 25-40 cycles

Gel Electrophoresis
Separates DNA fragments by size using electric current.
Agarose gel concentrations:
- 0.8-1.0% for large fragments (>1kb)
- 1.5-2.0% for small fragments (<1kb)
- Polyacrylamide for high resolution

Cloning Techniques:
- Restriction enzyme digestion
- Ligation reactions
- Transformation into competent cells
- Blue-white screening
- Colony PCR for verification

Protein Expression and Purification:
- Bacterial expression systems (E. coli)
- Eukaryotic expression (yeast, mammalian)
- Affinity chromatography
- Size exclusion chromatography
- Ion exchange chromatography

Western Blotting:
1. SDS-PAGE protein separation
2. Transfer to nitrocellulose membrane
3. Blocking with milk or BSA
4. Primary antibody incubation
5. Secondary antibody detection
6. Chemiluminescent visualization

Cell Culture Techniques:
- Sterile technique maintenance
- Media preparation and sterilization
- Cell passaging and counting
- Cryopreservation methods
- Contamination prevention

Microscopy Methods:
- Bright field microscopy
- Fluorescence microscopy
- Confocal microscopy
- Electron microscopy (SEM/TEM)
- Live cell imaging

Gene Expression Analysis:
- Northern blotting
- RT-PCR and qRT-PCR
- RNA sequencing (RNA-seq)
- Microarray analysis
- In situ hybridization

CRISPR-Cas9 Gene Editing:
- Guide RNA design
- Cas9 protein delivery
- Homology-directed repair
- Non-homologous end joining
- Off-target effect analysis
        """
    }
]

# Install reportlab if not available
try:
    from reportlab.pdfgen import canvas
except ImportError:
    os.system("pip install reportlab")
    from reportlab.pdfgen import canvas

# Create the PDFs
for pdf_info in test_pdfs:
    create_pdf(pdf_info["filename"], pdf_info["content"], pdf_info["title"])
    print(f"Created: {pdf_info['filename']}")

print("All test PDFs created successfully!")