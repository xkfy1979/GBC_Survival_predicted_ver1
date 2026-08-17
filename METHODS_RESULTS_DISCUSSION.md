# Methods

## Study population and outcomes

We performed a retrospective population-based analysis of patients with gallbladder cancer in the Surveillance, Epidemiology, and End Results (SEER) database. Eligible patients had an overall survival time greater than 0 months, valid numeric counts of examined and positive regional lymph nodes between 0 and 90, and a nonmissing regional lymph-node ratio. Overall survival was measured from diagnosis to death from any cause or last follow-up.

## Stage redefinitions and predictors

Three alternative nodal classifications were evaluated. In Redefined 1, recorded AJCC seventh-edition N0 disease remained N0, 1-2 positive nodes were classified as N1, and at least 3 positive nodes were classified as N2. In Redefined 2, recorded N0 remained N0, 1-3 positive nodes were classified as N1, and at least 4 positive nodes were classified as N2. In Redefined 3, recorded N0 remained N0, a lymph-node ratio greater than 0 and no greater than 0.40 was classified as N1, and a ratio greater than 0.40 and no greater than 1.00 was classified as N2. Unclassifiable cases were assigned NX. Stage groups were reconstructed using the derived AJCC seventh-edition T and M categories and each redefined N category. Stages IIIA and IIIB were combined as stage III, and stages IVA and IVB were combined as stage IV.

The modeling variables were stage group, age at diagnosis, sex, race, and histological grade. In the deployed interface, T, Redefined 2 N, and M are entered separately to derive the Redefined 2 stage group; they are not modeled as three additional independent covariates.

## Model development and validation

The cohort was divided into training and test sets in a 7:3 ratio using event-stratified random allocation and a random seed of 3. Continuous predictors were standardized and categorical predictors were one-hot encoded using parameters learned exclusively from the training set. Cox proportional hazards regression, Lasso-Cox, random survival forest, gradient boosting survival analysis, XGBoost-Cox, and survival support vector machine models were evaluated with the original AJCC seventh-edition stage and each redefined stage system.

Hyperparameters were optimized by five-fold cross-validation in the training set. The final model-stage combination was selected solely by the mean training-set cross-validated concordance index. Internal validation used five-fold out-of-fold predictions and 500 bootstrap resamples. Held-out test performance was quantified using Harrell's C-index, cumulative/dynamic AUCs at 1, 3, and 5 years, and Brier scores. Calibration was assessed by comparing predicted risk quintiles with Kaplan-Meier estimates, and clinical utility was explored using decision-curve analysis.

The selected XGBoost-Cox risk score was mapped to absolute survival using a one-dimensional Cox calibration model and a baseline cumulative hazard estimated in the training set. Median survival was defined as the earliest month at which the predicted survival probability was no greater than 0.50.

## Dynamic nomogram and web deployment

A Shiny for Python application was developed using the locked preprocessing pipeline, Redefined 2 stage algorithm, XGBoost-Cox model, and survival calibration function. The interface accepts age, sex, race, histological grade, T category, Redefined 2 N category, and M category and returns the derived stage, continuous risk score, predicted median survival, and 1-, 3-, and 5-year survival probabilities. Because XGBoost-Cox is a nonlinear ensemble model, the application was implemented as a dynamic nomogram-style calculator rather than a conventional additive point-based Cox nomogram.

# Results

A total of 1,114 patients met the eligibility criteria, including 820 deaths. The median age was 67 years. The training and independent test sets contained 779 and 335 patients, respectively. Under Redefined 2, 103 patients had stage I disease, 299 had stage II disease, 495 had stage III disease, 213 had stage IV disease, and 4 had an unknown stage.

Among 24 prespecified model-stage combinations, Redefined 2 plus XGBoost-Cox achieved the highest mean five-fold training C-index and was selected as the final model. Its mean cross-validated C-index was 0.732 (standard deviation, 0.031), and the out-of-fold C-index was 0.729 (95% confidence interval [CI], 0.709-0.751).

In the independent test set, the C-index was 0.703 (95% CI, 0.668-0.738). Time-dependent AUCs were 0.760 (95% CI, 0.706-0.815), 0.772 (95% CI, 0.716-0.823), and 0.804 (95% CI, 0.754-0.852) at 1, 3, and 5 years, respectively. Corresponding Brier scores were 0.177, 0.193, and 0.162. Calibration was generally acceptable, although risk was overestimated in selected low- and high-risk strata. In adjusted Cox comparisons, Redefined 2 did not significantly improve cross-validated discrimination relative to the original AJCC seventh-edition stage (difference in C-index, -0.0014; P = 0.560).

The Shiny implementation reproduced the locked model predictions. For the default demonstration profile (age 65 years, female, White race, grade II, T2, Redefined 2 N1, and M0), the derived classification was stage III, the risk score was 0.073, predicted median survival was 29 months, and predicted survival probabilities were 73.3%, 42.0%, and 27.5% at 1, 3, and 5 years, respectively.

# Discussion

The Redefined 2 plus XGBoost-Cox model provided the best cross-validated performance among the evaluated model-stage combinations and demonstrated moderate discrimination in the independent test set. Its increasing time-dependent AUC across longer horizons suggests that the combined demographic, pathological, and stage information can meaningfully distinguish longer-term survival risk.

XGBoost-Cox can capture nonlinear relationships and interactions that are not prespecified in conventional proportional hazards models. This flexibility may explain its favorable cross-validated performance. However, the reduction from the training cross-validated C-index to the test C-index indicates some optimism and reinforces the need for independent validation.

Redefined 2 offers a clinically intuitive separation between patients with 1-3 and at least 4 positive nodes. Nevertheless, it did not significantly outperform the original AJCC seventh-edition stage in adjusted Cox analysis. The findings therefore do not establish that Redefined 2 should replace the conventional AJCC system; instead, Redefined 2 functioned as one component of the best-performing machine-learning pipeline.

The dynamic Shiny application translates the nonlinear survival model into individualized absolute estimates without falsely representing XGBoost-Cox as a linear point-based nomogram. This approach improves usability, but the resulting probabilities remain dependent on the baseline event rate and follow-up distribution of the development cohort. Population-specific recalibration may be needed before use in other settings.

This study has several limitations. Its retrospective design introduces the potential for selection bias and residual confounding. SEER lacks consistent information on comorbidity, performance status, systemic therapy details, surgical quality, recurrence, molecular characteristics, and subsequent treatment. Calibration was imperfect in some test-set risk groups, and no geographic, temporal, prospective, or external validation was performed. The application is therefore intended for research use and should not replace multidisciplinary clinical judgment. External validation, recalibration, and prospective clinical-impact assessment are required before routine clinical implementation.
