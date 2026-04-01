import streamlit as st
import pandas as pd
from services.database import init_db
from services.expense_service import add_expense, get_expenses

# Initialize DB
init_db()

st.title("💰 Personal Expense Tracker")

# --- Load Data ---
raw = get_expenses()
df = pd.DataFrame(raw, columns=[
    "ID", "Date", "Category", "Amount", "Currency",
    "Converted Amount", "Split Type", "Participants", "Notes"
]) if raw else pd.DataFrame(columns=[
    "ID", "Date", "Category", "Amount", "Currency",
    "Converted Amount", "Split Type", "Participants", "Notes"
])

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

# --- Add Expense Form ---

# Success Toasts (persists across reruns)
if st.session_state.get("show_success"):
    st.success("Expense added!")
    st.session_state["show_success"] = False
# -----

# Init. Tabs
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Expense", "📋 Records", "📈 Analytics", "🎯 Budget Goals"])
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.header("Add New Expense")
        split_enabled = st.checkbox("Split this expense")

        with st.form("expense_form"):
            date = st.date_input("Date")
            currency = st.selectbox("Currency", ["SGD", "USD", "EUR", "JPY"])
            category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Other", "Monthly"])
            amount = st.number_input("Amount", min_value=0.0)

            rates = {
                "SGD": 1,
                "USD": 1.35,
                "EUR": 1.45,
                "JPY": 0.009
            }

            converted_amount = amount * rates[currency]
            st.write(f"Converted Amount (SGD): {converted_amount:.2f}")

            # Only show input if enabled
            if split_enabled:
                participants_input = st.text_input("Participants", "You,Alice,Bob")

            notes = st.text_input("Notes")

            submitted = st.form_submit_button("Add Expense")

            if submitted:
                try:
                    if split_enabled:
                        participants = [p.strip() for p in participants_input.split(",")]
                        split_type = "Equal Split"
                    else:
                        participants = ["You"]
                        split_type = "No Split"

                    # Expense now gets added to database
                    add_expense(
                        str(date),
                        category,
                        amount,
                        currency,
                        converted_amount,
                        split_type,
                        ",".join(participants),
                        notes
                    )

                    st.session_state["show_success"] = True  # Set flag before rerun
                    st.rerun()

                except Exception as e:
                    st.error(f"ERROR OCCURRED: {e}")

    df = pd.DataFrame(get_expenses(), columns=[
        "ID", "Date", "Category", "Amount", "Currency",
        "Converted Amount", "Split Type", "Participants", "Notes"
    ])

    with col2:
        st.header("Recent Expenses")

        if not df.empty:
            st.dataframe(df.head(9))




# Tab 2 - Records
with tab2:
    st.header("🔍 Filter & View Expenses")

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])

        # Filters
        category_filter = st.multiselect(
            "Select Category",
            options=df["Category"].unique(),
            default=df["Category"].unique()
        )

        date_range = st.date_input(
            "Select Date Range",
            [df["Date"].min(), df["Date"].max()]
        )

        # Apply filters
        filtered_df = df[
            (df["Category"].isin(category_filter)) &
            (df["Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
        ]
        st.dataframe(filtered_df.drop(columns=["ID"]), use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("Total Spent (SGD)", f"${filtered_df['Converted Amount'].sum():.2f}")
        col2.metric("Average Expense", f"${filtered_df['Converted Amount'].mean():.2f}")

        st.subheader("🗑️ Delete an Expense")
        if not filtered_df.empty:
            selected_id = st.selectbox("Select Expense ID", filtered_df["ID"].tolist())
            if st.button("Delete"):
                from services.expense_service import delete_expense

                delete_expense(selected_id)
                st.success("Deleted!")
                st.rerun()
    else:
        st.info("No expenses yet.")

# Tab 3 - Analytics
# --- Display Expenses ---
with tab3:
    st.header("📈 Analytics")

    if not df.empty:

        # --- Monthly Spending Trend ---
        st.subheader("Monthly Spending Trend")

        monthly = df.groupby(df["Date"].dt.to_period("M"))["Converted Amount"].sum()
        monthly.index = monthly.index.astype(str)
        st.line_chart(monthly)

        # --- Month-over-Month comparison ---
        if len(monthly) >= 2:
            last_month = monthly.iloc[-1]
            prev_month = monthly.iloc[-2]
            delta = last_month - prev_month
            st.metric(
                label=f"Spending in {monthly.index[-1]}",
                value=f"${last_month:.2f}",
                delta=f"${delta:+.2f} vs previous month",
                delta_color="inverse"
            )

        st.divider()

        # --- Spending Heatmap by Day of Week ---
        st.subheader("🗓️ Spending by Day of Week")

        df["DayOfWeek"] = df["Date"].dt.day_name()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        day_spend = (
            df.groupby("DayOfWeek")["Converted Amount"]
            .sum()
            .reindex(day_order, fill_value=0)
        )

        st.bar_chart(day_spend)

        # Highlight peak day
        peak_day = day_spend.idxmax()
        st.caption(f"📌 You tend to spend the most on **{peak_day}**s (SGD ${day_spend[peak_day]:.2f} total)")

        st.divider()

        # --- Spending by Category ---
        st.subheader("Spending by Category")
        category_sum = df.groupby("Category")["Converted Amount"].sum().sort_values(ascending=False)
        st.bar_chart(category_sum)

    else:
        st.info("No data to analyse yet.")

# ─────────────────────────────────────────────
# TAB 4 — Budget Goals
# ─────────────────────────────────────────────
with tab4:
    st.header("🎯 Budget Goals")

    # --- Overall Monthly Budget ---
    st.subheader("Overall Monthly Budget")

    overall_budget = st.number_input(
        "Set your total monthly budget (SGD)", min_value=0.0,
        value=st.session_state.get("overall_budget", 2000.0),
        key="overall_budget"
    )

    if not df.empty and overall_budget > 0:
        current_month = pd.Timestamp.now().to_period("M")
        this_month_df = df[df["Date"].dt.to_period("M") == current_month]
        month_total = this_month_df["Converted Amount"].sum()
        ratio = min(month_total / overall_budget, 1.0)
        over = month_total > overall_budget

        st.metric(
            "Spent this month",
            f"${month_total:.2f}",
            delta=f"${month_total - overall_budget:.2f} over budget" if over else f"${overall_budget - month_total:.2f} remaining",
            delta_color="inverse"
        )
        st.progress(ratio)
        if over:
            st.error(f"⚠️ You've exceeded your monthly budget by ${month_total - overall_budget:.2f}!")

    st.divider()

    # --- Per-Category Budgets ---
    st.subheader("Per-Category Budgets")

    categories = ["Food", "Transport", "Shopping", "Other", "Monthly"]

    if "cat_budgets" not in st.session_state:
        st.session_state["cat_budgets"] = {c: 0.0 for c in categories}

    cols = st.columns(2)
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            st.session_state["cat_budgets"][cat] = st.number_input(
                f"{cat} budget (SGD/month)",
                min_value=0.0,
                value=st.session_state["cat_budgets"][cat],
                key=f"budget_{cat}"
            )

    st.subheader("Progress")

    if not df.empty:
        current_month = pd.Timestamp.now().to_period("M")
        this_month_df = df[df["Date"].dt.to_period("M") == current_month]

        for cat in categories:
            budget = st.session_state["cat_budgets"][cat]
            if budget <= 0:
                continue

            spent = this_month_df[this_month_df["Category"] == cat]["Converted Amount"].sum()
            ratio = min(spent / budget, 1.0)
            over = spent > budget

            label = f"{cat}: ${spent:.2f} / ${budget:.2f}"
            if over:
                st.markdown(f"🔴 **{label} — OVER BUDGET**")
            else:
                st.markdown(f"🟢 **{label}**")
            st.progress(ratio)
    else:
        st.info("Add some expenses to track progress against your budgets.")