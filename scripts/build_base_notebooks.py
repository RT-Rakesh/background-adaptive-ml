"""Build the two base notebooks with proper cell tags.

Run once:  python scripts/build_base_notebooks.py
Outputs:   notebooks/01_simple_regression.ipynb
           notebooks/02_deep_learning_regression.ipynb

Tags drive the adaptation skill — see skill/canonical_terms.yaml and
.github/skills/adapt-notebook/SKILL.md.

Two-tier locking (May 2026 redesign):
  - lock:terms       — narrative-free canonical definitions; byte-identical
                       across all personas.
  - keep:code        — code cells; byte-identical across all personas.
  - adapt:narrative  — title / story / section-intro markdown; persona-
                       specific (not byte-locked).
  - adapt:{intro,explanation,example,exercise,suggestions,code-comment}
                     — per-cell adapter targets.
  - inject:glossary  — placeholder replaced by the skill.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "notebooks"
OUT.mkdir(exist_ok=True)

_id_counter = 0


def _next_id(source: str) -> str:
    global _id_counter
    _id_counter += 1
    h = hashlib.sha1(f"{_id_counter}:{source}".encode()).hexdigest()[:8]
    return f"cell-{_id_counter:03d}-{h}"


def md(source: str, *tags: str) -> dict:
    body = dedent(source).strip("\n").splitlines(keepends=True)
    return {
        "cell_type": "markdown",
        "id": _next_id(source),
        "metadata": {"tags": list(tags)},
        "source": body,
    }


def code(source: str, *tags: str) -> dict:
    body = dedent(source).strip("\n").splitlines(keepends=True)
    return {
        "cell_type": "code",
        "id": _next_id(source),
        "metadata": {"tags": list(tags)},
        "source": body,
        "execution_count": None,
        "outputs": [],
    }


def write_notebook(path: Path, cells: list[dict], sections: list[str]) -> None:
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
            "adapt_sections": sections,
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Shared placeholders
# ---------------------------------------------------------------------------

GLOSSARY_PLACEHOLDER = """\
> **Glossary cell — replaced by the adaptation skill.**
>
> When you run the `adapt-notebook` skill, this cell is replaced with a small
> table mapping vocabulary from your field to the ML terms used below.
> If you have not run the skill, you can safely ignore this cell.
"""

SUGGESTIONS_PLACEHOLDER = """\
### Go deeper with an LLM (optional — skip if you already know this)

The adaptation skill replaces this block with 2–4 copy-pasteable prompts
tailored to your background. Paste them into ChatGPT / Claude / Mistral /
your preferred model, explore the idea, then come back here and continue.
"""


# ---------------------------------------------------------------------------
# Notebook 01 — Simple Linear Regression
# ---------------------------------------------------------------------------

nb01 = [
    # 0
    md(
        """
        # Simple Linear Regression — *placeholder title*

        A first machine learning notebook. The adaptation skill will rewrite
        this title and the story below to match your field; the canonical
        definitions, formulas, and code stay the same for everyone.
        """,
        "adapt:narrative",
    ),
    # 1
    md(
        """
        ## The story

        Imagine you have a single measured quantity `x` and you want to
        predict another quantity `y` from it. From past observations you
        have a list of `(x, y)` pairs.

        Our job: learn a rule that turns `x` into a prediction of `y`, so
        next time we can act with confidence.
        """,
        "adapt:narrative",
    ),
    # 2
    md(GLOSSARY_PLACEHOLDER, "inject:glossary"),
    # 3
    code(
        """
        import numpy as np
        import matplotlib.pyplot as plt

        rng = np.random.default_rng(42)
        """,
        "keep:code",
    ),
    # 4
    md(
        """
        ## 1. Setting the scene

        In this notebook each observation is a pair `(x, y)`. The skill's
        glossary cell above tells you what `x` and `y` mean in *your* field.
        The next cell defines the ML vocabulary we will use throughout.
        """,
        "adapt:narrative",
    ),
    # 5 — pure vocabulary, no story, byte-locked.
    md(
        """
        ### Core vocabulary

        - **feature** — the input variable, here `x`.
        - **target** — the quantity we want to predict, here `y`.
        - A dataset is a collection of `(feature, target)` pairs.
        - **training data** — the subset used to fit the model.
        - **test data** — the subset held back to evaluate the model honestly.
        - **train/test split** — the act of partitioning the dataset into
          training data and test data.
        """,
        "lock:terms",
    ),
    # 6 — field-specific bridge for the vocabulary above.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to spell out — in your
        field's own units and routines — what *this* `x` and *this* `y`
        actually represent, what your training data and test data look
        like in practice, and how a train/test split would look on your
        own data.
        """,
        "adapt:context",
    ),
    # 7
    code(
        """
        # Synthetic ground truth: y = 0.25 * x + 1.0 + small noise
        true_slope = 0.25
        true_intercept = 1.0

        x_data = rng.uniform(10, 200, size=80)
        noise = rng.normal(0, 3.0, size=x_data.shape)
        y_data = true_slope * x_data + true_intercept + noise
        """,
        "keep:code",
    ),
    # 7
    code(
        """
        # Plot the raw data: each dot is one past observation.
        plt.figure(figsize=(6, 4))
        plt.scatter(x_data, y_data, alpha=0.7)
        plt.xlabel("feature x")
        plt.ylabel("target y")
        plt.title("Past observations")
        plt.grid(True, alpha=0.3)
        plt.show()
        """,
        "adapt:code-comment",
    ),
    # 8
    md(
        """
        ### What pattern do you see?

        The cloud of points slopes upward: larger `x`, larger `y`. Our goal
        is to draw the *best straight line* through that cloud, so that for
        a new value of `x` we can read off a prediction of `y` from the line.
        """,
        "adapt:explanation",
    ),
    # 9
    md(SUGGESTIONS_PLACEHOLDER, "adapt:suggestions"),
    # 10 — model equation, byte-locked.
    md(
        """
        ## 2. The model — linear regression

        A **linear regression model** is the rule

        $$ \\hat{y} = w \\cdot x + b $$

        where $x$ is the feature, $\\hat{y}$ is the **prediction**, and $w$
        and $b$ are numbers the model learns. They are called the model's
        **parameters** (or **weights**, with $b$ specifically called the
        **bias**). A small set of parameters that fits a lot of data — that
        is the whole idea of regression.
        """,
        "lock:terms",
    ),
    # 12 — field-specific bridge for the model equation above.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to say what `w` (the
        slope) and `b` (the bias) actually mean in your own work — in
        units and quantities you handle every day — so the equation
        $\\hat{y} = w \\cdot x + b$ is no longer abstract.
        """,
        "adapt:context",
    ),
    # 13
    md(
        """
        ### Worked example

        With `w = 0.24` and `b = 1.1`, for `x = 100` the prediction is
        `0.24 * 100 + 1.1 = 25.1`. The skill will rewrite this cell with a
        worked example phrased in your field's units.
        """,
        "adapt:example",
    ),
    # 12
    code(
        """
        from sklearn.linear_model import LinearRegression

        X = x_data.reshape(-1, 1)   # sklearn expects a 2-D feature matrix
        y = y_data

        model = LinearRegression().fit(X, y)
        learned_slope = float(model.coef_[0])
        learned_intercept = float(model.intercept_)
        learned_slope, learned_intercept
        """,
        "keep:code",
    ),
    # 13
    md(
        """
        The two numbers above are the learned parameters. Compare them with
        the ground-truth slope (`0.25`) and intercept (`1.0`) — the model
        has recovered the underlying rule from noisy data.
        """,
        "adapt:explanation",
    ),
    # 14 — loss definition, byte-locked.
    md(
        """
        ## 3. How good is the fit? — the loss

        For each training point we compute the **residual**, the gap between
        the true target and the prediction:

        $$ r_i = y_i - \\hat{y}_i $$

        Squaring and averaging gives the **mean squared error (MSE)**, the
        most common **loss** for regression:

        $$ \\text{MSE} = \\frac{1}{N} \\sum_{i=1}^{N} (y_i - \\hat{y}_i)^2 $$

        A smaller loss means a better fit. "Training a model" is the search
        for parameters that minimise the loss.
        """,
        "lock:terms",
    ),
    # 17 — field-specific bridge for the loss / MSE.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to say what a **residual**
        and the **MSE** correspond to in *your* work — the gap between
        what you expected and what actually happened, summed up across
        every past observation.
        """,
        "adapt:context",
    ),
    # 18
    code(
        """
        y_pred = model.predict(X)
        residuals = y - y_pred
        mse = float(np.mean(residuals ** 2))
        print(f"MSE = {mse:.3f}")
        """,
        "keep:code",
    ),
    # 16
    md(SUGGESTIONS_PLACEHOLDER, "adapt:suggestions"),
    # 17 — gradient descent definition, byte-locked.
    md(
        """
        ## 4. Gradient descent — learning by tiny steps

        sklearn solved for the best `w, b` in one shot using linear algebra.
        For larger models we cannot do that, so we use **gradient descent**.

        The **gradient** of the loss with respect to a parameter tells us
        which direction makes the loss grow. We step in the opposite
        direction. We repeat for many **epochs** (one epoch = one full pass
        over the training data), each time moving the parameters a small
        amount controlled by the **learning rate**.
        """,
        "lock:terms",
    ),
    # 21 — field-specific bridge for gradient descent.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to ground gradient descent
        and the learning rate in something you do every day — adjusting a
        recipe, tuning an instrument, refining an estimate — so that
        "step downhill in the direction of the negative gradient" stops
        sounding like jargon.
        """,
        "adapt:context",
    ),
    # 22
    code(
        """
        # From-scratch gradient descent for the same problem.
        w, b = 0.0, 0.0          # start anywhere
        learning_rate = 1e-6     # small steps so the descent is visible
        epochs = 8000
        history = []

        for epoch in range(epochs):
            y_hat = w * x_data + b
            error = y_hat - y_data                  # shape (N,)
            grad_w = 2 * np.mean(error * x_data)
            grad_b = 2 * np.mean(error)
            w -= learning_rate * grad_w
            b -= learning_rate * grad_b
            history.append(np.mean(error ** 2))

        print(f"learned w = {w:.3f}, b = {b:.3f}")
        print(f"final MSE = {history[-1]:.3f}")
        """,
        "keep:code",
    ),
    # 19
    code(
        """
        # Watch the loss fall as training progresses.
        # Log-scale on the y-axis spreads the descent across the whole plot,
        # so we can see the slow grind that follows the initial big drop.
        plt.figure(figsize=(6, 4))
        plt.semilogy(history)
        plt.xlabel("epoch")
        plt.ylabel("MSE (loss, log scale)")
        plt.title("Loss curve during gradient descent")
        plt.grid(True, which="both", alpha=0.3)
        plt.show()
        """,
        "adapt:code-comment",
    ),
    # 20
    md(
        """
        ### Why this matters

        Every modern deep-learning model — no matter how large — is trained
        with some flavour of gradient descent. The learning rate controls
        how bold each step is: too small and training crawls; too large and
        it overshoots and never settles.
        """,
        "adapt:explanation",
    ),
    # 21
    md(SUGGESTIONS_PLACEHOLDER, "adapt:suggestions"),
    # 22 — train/test, over/underfitting definitions, byte-locked.
    md(
        """
        ## 5. Honest evaluation — train/test split

        A model that memorises the training data is not useful. To check
        whether it has truly learned the *pattern*, we hide some data
        during training and only look at it at the end. That hidden portion
        is the **test data**.

        - **Underfitting**: the model is too simple to capture the pattern;
          loss is high on both training data and test data.
        - **Overfitting**: the model has memorised noise; training loss is
          low but test loss is high.
        """,
        "lock:terms",
    ),
    # 27 — field-specific bridge for honest evaluation.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to describe — in your
        own working language — what overfitting and underfitting feel
        like on *your* data, and why holding some past observations back
        for an honest check is worth the effort.
        """,
        "adapt:context",
    ),
    # 28
    code(
        """
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=0
        )
        m = LinearRegression().fit(X_train, y_train)

        train_mse = float(np.mean((y_train - m.predict(X_train)) ** 2))
        test_mse = float(np.mean((y_test - m.predict(X_test)) ** 2))
        print(f"train MSE = {train_mse:.3f}")
        print(f" test MSE = {test_mse:.3f}")
        """,
        "keep:code",
    ),
    # 24
    md(
        """
        ## Try this yourself

        1. Re-run the data-generation cell with a larger `noise` standard
           deviation. What happens to the MSE? To the recovered slope?
        2. Set the learning rate to `1e-3` in the gradient-descent cell.
           Does training still converge? Why or why not?
        3. Reduce the dataset to the first 10 points and rerun. Compare
           train MSE and test MSE — do you see overfitting?
        """,
        "adapt:exercise",
    ),
    # 25 — recap vocabulary list, byte-locked.
    md(
        """
        ## Recap — vocabulary you now own

        **feature**, **target**, **training data**, **test data**,
        **train/test split**, **model**, **parameters**, **weights**,
        **bias**, **prediction**, **residual**, **loss**,
        **mean squared error**, **MSE**, **gradient**, **gradient descent**,
        **learning rate**, **epoch**, **overfitting**, **underfitting**.
        """,
        "lock:terms",
    ),
    # 26
    md(
        """
        Up next: a small **neural network** that predicts something harder
        than a single straight line.
        """,
        "adapt:narrative",
    ),
]

write_notebook(OUT / "01_simple_regression.ipynb", nb01, sections=["regression"])


# ---------------------------------------------------------------------------
# Notebook 02 — Deep Learning Regression (tiny PyTorch MLP)
# ---------------------------------------------------------------------------

nb02 = [
    # 0
    md(
        """
        # Deep Learning Regression — *placeholder title*

        In notebook 01 we predicted `y` from a single feature `x` with a
        straight line. Some relationships are **non-linear**: the right
        amount of one input is good, twice as much is bad. A
        **neural network** is the natural tool for those.
        """,
        "adapt:narrative",
    ),
    # 1
    md(
        """
        ## The story, extended

        Each observation now has **four features** (we will call them
        `f1, f2, f3, f4`) and one target `y`. Some features interact
        non-linearly. The skill's glossary cell above tells you what each
        feature and the target mean in your field.
        """,
        "adapt:narrative",
    ),
    # 2
    md(GLOSSARY_PLACEHOLDER, "inject:glossary"),
    # 3
    code(
        """
        import numpy as np
        import torch
        import torch.nn as nn
        import matplotlib.pyplot as plt

        torch.manual_seed(0)
        rng = np.random.default_rng(0)
        """,
        "keep:code",
    ),
    # 4
    md(
        """
        ## 1. The data

        Each row is one past observation. The four columns are the
        **features** `f1, f2, f3, f4` (here scaled to 0–1) and the column
        we want to predict is the **target** `y`.
        """,
        "adapt:narrative",
    ),
    # 5 — multi-feature framing, byte-locked.
    md(
        """
        ### From one feature to many

        We now have a feature *vector* per observation, not a single number.
        The model still produces one **prediction** per observation; it just
        has more inputs to combine.
        """,
        "lock:terms",
    ),
    # field-specific bridge for multi-feature framing.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to say what each of the
        four features `f1, f2, f3, f4` represents in your work — four
        quantities you would actually measure or look up about a single
        case — and what `y` is when those four come together.
        """,
        "adapt:context",
    ),
    # data
    code(
        """
        N = 800
        X = rng.uniform(0, 1, size=(N, 4)).astype(np.float32)
        f1, f2, f3, f4 = X[:, 0], X[:, 1], X[:, 2], X[:, 3]

        # Non-linear ground truth: a smooth function with interactions.
        y_true = (
            5.0
            + 3.0 * np.sin(2 * np.pi * f1)
            + 4.0 * (f2 * f3)
            - 6.0 * (f4 - 0.4) ** 2
            + rng.normal(0, 0.3, size=N).astype(np.float32)
        )
        y = y_true.astype(np.float32)
        X.shape, y.shape
        """,
        "keep:code",
    ),
    # 7
    md(
        """
        A linear model cannot capture this — `y` is not a straight-line
        function of any single feature. We need a model that can learn
        curves and interactions between features.
        """,
        "adapt:explanation",
    ),
    # 8
    md(SUGGESTIONS_PLACEHOLDER, "adapt:suggestions"),
    # 9 — neural network definition, byte-locked.
    md(
        """
        ## 2. The model — a small neural network

        A **neural network** stacks layers of simple computations.
        Each **hidden layer** computes `h = activation(W · x + b)`, where
        `W` and `b` are learnable **weights** and **bias** and the
        **activation function** is a **non-linearity** such as **ReLU**
        ($\\text{ReLU}(z) = \\max(0, z)$). Without an activation function,
        stacking layers would still only give you a linear model.

        Our network has 4 inputs → 16 hidden units → 16 hidden units → 1
        output (the predicted target).
        """,
        "lock:terms",
    ),
    # field-specific bridge for the neural network architecture.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to describe the network
        in your own terms — what each hidden layer is doing as it mixes
        the four field-specific inputs, and why a stack of small
        non-linear steps lets the model bend in ways a single rule of
        thumb cannot.
        """,
        "adapt:context",
    ),
    # worked example
    md(
        """
        ### Worked example

        Each hidden unit can be thought of as one specialist paying
        attention to a particular combination of features. The next layer
        combines the specialists' opinions into a final prediction. The
        skill will rewrite this analogy in your field's terms.
        """,
        "adapt:example",
    ),
    # 11
    code(
        """
        class RegressionNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(4, 16),
                    nn.ReLU(),
                    nn.Linear(16, 16),
                    nn.ReLU(),
                    nn.Linear(16, 1),
                )

            def forward(self, x):
                return self.layers(x).squeeze(-1)

        net = RegressionNet()
        sum(p.numel() for p in net.parameters())   # total parameters
        """,
        "keep:code",
    ),
    # 12 — training loop definitions, byte-locked.
    md(
        """
        ## 3. Training — forward pass, loss, backward pass

        Training one **batch** of data has three steps:

        1. **Forward pass** — feed the features through the network to get
           predictions.
        2. Compute the **loss** (MSE again) by comparing predictions to
           targets.
        3. **Backward pass** (also called **backpropagation**) — compute
           the **gradient** of the loss with respect to every weight, then
           ask the **optimizer** to nudge the weights one step.

        We repeat for many **epochs** until the loss stops improving.
        """,
        "lock:terms",
    ),
    # field-specific bridge for the training loop.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to put the forward pass,
        loss, backward pass, and optimizer step into your own working
        rhythm — the equivalent of "try, check the gap, adjust, try
        again" you already use in your day job, just done thousands of
        times automatically.
        """,
        "adapt:context",
    ),
    # train/test split code
    code(
        """
        # Train/test split.
        idx = rng.permutation(N)
        n_train = int(0.8 * N)
        train_idx, test_idx = idx[:n_train], idx[n_train:]

        X_train = torch.tensor(X[train_idx])
        y_train = torch.tensor(y[train_idx])
        X_test  = torch.tensor(X[test_idx])
        y_test  = torch.tensor(y[test_idx])
        """,
        "keep:code",
    ),
    # 14
    code(
        """
        loss_fn = nn.MSELoss()
        optimizer = torch.optim.Adam(net.parameters(), lr=1e-2)

        epochs = 300
        batch_size = 64
        history = []

        for epoch in range(epochs):
            perm = torch.randperm(X_train.shape[0])
            epoch_loss = 0.0
            for start in range(0, X_train.shape[0], batch_size):
                b = perm[start:start + batch_size]
                pred = net(X_train[b])                  # forward pass
                loss = loss_fn(pred, y_train[b])
                optimizer.zero_grad()
                loss.backward()                          # backward pass
                optimizer.step()
                epoch_loss += float(loss) * b.shape[0]
            history.append(epoch_loss / X_train.shape[0])

        print(f"final train MSE = {history[-1]:.3f}")
        """,
        "keep:code",
    ),
    # 15
    code(
        """
        # The loss curve: each point is the average MSE for one full epoch.
        plt.figure(figsize=(6, 4))
        plt.plot(history)
        plt.xlabel("epoch")
        plt.ylabel("MSE (loss)")
        plt.title("Training the regression network")
        plt.grid(True, alpha=0.3)
        plt.show()
        """,
        "adapt:code-comment",
    ),
    # 16
    md(SUGGESTIONS_PLACEHOLDER, "adapt:suggestions"),
    # 17 — overfitting definition (DL flavour), byte-locked.
    md(
        """
        ## 4. Did it actually learn?

        We now look at the **test data** the network has never seen.
        If the test MSE is close to the training MSE, the model has learned
        a generalisable rule, not just memorised. If the test MSE is much
        higher, we have **overfitting** — the same enemy as in notebook 01,
        only sneakier in deep models with many parameters.
        """,
        "lock:terms",
    ),
    # field-specific bridge for honest evaluation.
    md(
        """
        ### In your field

        The adaptation skill rewrites this cell to describe — in your
        own working language — what overfitting looks like on *your*
        data when the network has many parameters and only a modest pile
        of past observations to learn from.
        """,
        "adapt:context",
    ),
    # eval code
    code(
        """
        with torch.no_grad():
            test_pred = net(X_test)
            test_mse = float(loss_fn(test_pred, y_test))
        print(f"test MSE = {test_mse:.3f}")

        plt.figure(figsize=(5, 5))
        plt.scatter(y_test.numpy(), test_pred.numpy(), alpha=0.6)
        lims = [float(y_test.min()) - 0.5, float(y_test.max()) + 0.5]
        plt.plot(lims, lims, "k--", alpha=0.5)
        plt.xlabel("true target y")
        plt.ylabel("predicted target y")
        plt.title("Predictions vs truth (test set)")
        plt.grid(True, alpha=0.3)
        plt.show()
        """,
        "keep:code",
    ),
    # 19
    md(
        """
        Points clustered along the diagonal mean the network has captured
        the non-linear interactions between features. A linear regression
        on the same data would leave a much messier scatter.
        """,
        "adapt:explanation",
    ),
    # 20
    md(SUGGESTIONS_PLACEHOLDER, "adapt:suggestions"),
    # 21
    md(
        """
        ## Try this yourself

        1. Reduce the network to a single `nn.Linear(4, 1)` (no hidden
           layer, no activation function). How much worse is the test MSE?
           Why?
        2. Increase the learning rate to `0.5`. What happens to the loss
           curve?
        3. Replace `nn.ReLU()` with `nn.Tanh()`. Does it train as well?
        """,
        "adapt:exercise",
    ),
    # 22 — recap vocab, byte-locked.
    md(
        """
        ## Recap — vocabulary you now own

        On top of notebook 01: **neural network**, **hidden layer**,
        **activation function**, **ReLU**, **forward pass**,
        **backward pass**, **backpropagation**, **optimizer**, **batch**,
        **non-linearity**.
        """,
        "lock:terms",
    ),
    # 23
    md(
        """
        The training loop — forward, loss, backward, step — is the same
        loop that powers every modern model, from a 4-input regressor like
        this one to a 100-billion-parameter language model.
        """,
        "adapt:narrative",
    ),
]

write_notebook(OUT / "02_deep_learning_regression.ipynb", nb02, sections=["deep_learning"])
