"""
The following code was adapted from the Bank Reserves model included in Netlogo
Model information can be found at: http://ccl.northwestern.edu/netlogo/models/BankReserves
Accessed on: November 2, 2017
Author of NetLogo code:
    Wilensky, U. (1998). NetLogo Bank Reserves model.
    http://ccl.northwestern.edu/netlogo/models/BankReserves.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import mesa

from bank_reserves.random_walk import RandomWalker


class Bank(mesa.Agent):
    def __init__(self, unique_id, model, reserve_percent=50, 
                 deposit_interest=1, loan_interest=2, risk_preference=0.5):
        # initialize the parent class with required parameters
        super().__init__(unique_id, model)
        # for tracking total value of loans outstanding
        self.bank_loans = 0
        """percent of deposits the bank must keep in reserves - this is set via
           Slider in server.py"""
        self.reserve_percent = reserve_percent
        # for tracking total value of deposits
        self.deposits = 0
        # total amount of deposits in reserve
        self.reserves = (self.reserve_percent / 100) * self.deposits
        # amount the bank is currently able to loan
        self.bank_to_loan = 0
        # amount the bank net worth (cumulative profit)
        self.net_wealth = 0
        # interest payment rate to their customers
        self.deposit_interest = deposit_interest
        # interest rate of their loan
        self.loan_interest = loan_interest
        # investment to risky asset
        self.risk_asset = 0
        # risk preference of the bank
        self.risk_preference = risk_preference


    """update the bank's reserves and amount it can loan;
       this is called every time a person balances their books
       see below for Person.balance_books()"""
    def bank_balance(self):
        self.reserves = (self.reserve_percent / 100) * self.deposits
        self.bank_to_loan = self.deposits - (self.reserves + self.bank_loans + self.risk_asset)
        
    """before step of household, bank investments to risky asset from their money it can loan"""
    def invest_risky_asset(self):
        # buy risk asset
        self.risk_asset = self.bank_to_loan * self.risk_preference
        self.bank_to_loan -= self.risk_asset
    
    """ after step of household, bank get profit or loss from their investment"""
    def get_result_from_investment(self):
        # get prifit pct . it is drown from gauss distribution
        investment_profit_pct = self.random.gauss(self.model.risk_mu, self.model.risk_sigma)
        # increase or decrease the amount of all risk asset depends on the profit pct
        self.deposits += self.risk_asset * (investment_profit_pct / 100)


# subclass of RandomWalker, which is subclass to Mesa Agent
class Person(RandomWalker):
    def __init__(self, unique_id, pos, model, moore, bank, rich_threshold):
        # init parent class with required parameters
        super().__init__(unique_id, pos, model, moore=moore)
        # the amount each person has in savings
        self.savings = 0
        # total loan amount person has outstanding
        self.loans = 0
        # total risky asset
        self.risk_asset = 0
        """start everyone off with a random amount in their wallet from 1 to a
           user settable rich threshold amount"""
        self.wallet = self.random.randint(1, rich_threshold + 1)
        # savings minus loans, see balance_books() below
        self.wealth = 0
        # person to trade with, see do_business() below
        self.customer = 0
        # person's bank, set at __init__, all people have the same bank in this model
        self.bank = bank

    def do_business(self):
        """check if person has any savings, any money in wallet, or if the
        bank can loan them any money"""
        if self.savings > 0 or self.wallet > 0 or self.bank.bank_to_loan > 0:
            # create list of people at my location (includes self)
            my_cell = self.model.grid.get_cell_list_contents([self.pos])
            # check if other people are at my location
            if len(my_cell) > 1:
                # set customer to self for while loop condition
                customer = self
                while customer == self:
                    """select a random person from the people at my location
                    to trade with"""
                    customer = self.random.choice(my_cell)
                # 50% chance of trading with customer
                if self.random.randint(0, 1) == 0:
                    # 50% chance of trading $5
                    if self.random.randint(0, 1) == 0:
                        # give customer $5 from my wallet (may result in negative wallet)
                        customer.wallet += 5
                        self.wallet -= 5
                    # 50% chance of trading $2
                    else:
                        # give customer $2 from my wallet (may result in negative wallet)
                        customer.wallet += 2
                        self.wallet -= 2

    def balance_books(self):
        # check if wallet is negative from trading with customer
        if self.wallet < 0:
            # if negative money in wallet, check if my savings can cover the balance
            if self.savings >= (self.wallet * -1):
                """if my savings can cover the balance, withdraw enough
                money from my savings so that my wallet has a 0 balance"""
                self.withdraw_from_savings(self.wallet * -1)
            # if my savings cannot cover the negative balance of my wallet
            else:
                # check if i have any savings
                if self.savings > 0:
                    """if i have savings, withdraw all of it to reduce my
                    negative balance in my wallet"""
                    self.withdraw_from_savings(self.savings)
                # record how much money the bank can loan out right now
                temp_loan = self.bank.bank_to_loan
                """check if the bank can loan enough money to cover the
                   remaining negative balance in my wallet"""
                if temp_loan >= (self.wallet * -1):
                    """if the bank can loan me enough money to cover
                    the remaining negative balance in my wallet, take out a
                    loan for the remaining negative balance"""
                    self.take_out_loan(self.wallet * -1)
                else:
                    """if the bank cannot loan enough money to cover the negative
                    balance of my wallet, then take out a loan for the
                    total amount the bank can loan right now"""
                    self.take_out_loan(temp_loan)
        else:
            """if i have money in my wallet from trading with customer, deposit
            it to my savings in the bank"""
            self.deposit_to_savings(self.wallet)
        # check if i have any outstanding loans, and if i have savings
        if self.loans > 0 and self.savings > 0:
            # check if my savings can cover my outstanding loans
            if self.savings >= self.loans:
                # payoff my loans with my savings
                self.withdraw_from_savings(self.loans)
                self.repay_a_loan(self.loans)
            # if my savings won't cover my loans
            else:
                # pay off part of my loans with my savings
                self.withdraw_from_savings(self.savings)
                self.repay_a_loan(self.wallet)
        # calculate my wealth
        self.wealth = self.savings + self.risk_asset - self.loans

    # part of balance_books()
    def deposit_to_savings(self, amount):
        # take money from my wallet and put it in savings
        self.wallet -= amount
        self.savings += amount
        # increase bank deposits
        self.bank.deposits += amount

    # part of balance_books()
    def withdraw_from_savings(self, amount):
        # put money in my wallet from savings
        self.wallet += amount
        self.savings -= amount
        # decrease bank deposits
        self.bank.deposits -= amount

    # part of balance_books()
    def repay_a_loan(self, amount):
        # take money from my wallet to pay off all or part of a loan
        self.loans -= amount
        self.wallet -= amount
        # increase the amount the bank can loan right now
        self.bank.bank_to_loan += amount
        # decrease the bank's outstanding loans
        self.bank.bank_loans -= amount

    # part of balance_books()
    def take_out_loan(self, amount):
        """borrow from the bank to put money in my wallet, and increase my
        outstanding loans"""
        self.loans += amount
        self.wallet += amount
        # decresae the amount the bank can loan right now
        self.bank.bank_to_loan -= amount
        # increase the bank's outstanding loans
        self.bank.bank_loans += amount
    
    def settlement(self):
        if self.savings > 0:
            self.get_interest_payment()
        if self.loans > 0:
            self.pay_interest_payment()
        if self.risk_asset > 0:
            self.sell_risk_asset()
    
    # part of settlement()
    def get_interest_payment(self):
        """ If i have positive bank deposit, they can get interest payment
        from their bank"""
        interest_payment_from_bank = self.savings * (self.bank.deposit_interest/100)
        # get interest payment if bank can pay the amount
        if interest_payment_from_bank < self.bank.bank_to_loan:
            # household get money
            self.savings += interest_payment_from_bank
            # total deposit increase
            self.bank.deposits += interest_payment_from_bank
            # banks money decrease
            self.bank.bank_to_loan -= interest_payment_from_bank

    
    def pay_interest_payment(self):
        """ If i have bank loan, the loan increase bacause the interest payment
        to their bank"""
        interest_payment_to_bank = self.loans * (self.bank.loan_interest/100)
        # get interest payment
        self.loans += interest_payment_to_bank
        # bank total outstanding loan increase
        #self.bank.bank_loans += interest_payment_to_bank

    def sell_risk_asset(self):
        # get prifit pct . it is drown from gauss distribution
        investment_profit_pct = self.random.gauss(self.model.risk_mu, self.model.risk_sigma)
        # increase or decrease the amount of all risk asset depends on the profit pct
        self.risk_asset += self.risk_asset * (investment_profit_pct / 100)
        # return their profit to bank deposit
        self.savings += self.risk_asset
        self.bank.deposits += self.risk_asset
        self.risk_asset = 0
        #print(f'i am rich so i investment {money_for_investment}')

    def investment(self):
        """ If i is rich, they start buy risky asset"""
        if self.wealth > self.model.rich_threshold:
            # deside the amount of the investment
            self.money_for_investment = self.savings *0.2 # 0.2 is hard cording
            # take out the money from their bank to investment
            self.savings -= self.money_for_investment
            self.bank.deposits -= self.money_for_investment
            # buy risky asset
            self.risk_asset += self.money_for_investment
            self.money_for_investment = 0
        
    # step is called for each agent in model.BankReservesModel.schedule.step()
    def step(self):
        # settlement their loan and deposit interest payment
        self.settlement()
        # move to a cell in my Moore neighborhood
        self.random_move()
        # trade
        self.do_business()
        # deposit money or take out a loan
        self.balance_books()
        # make investment if they are rich
        self.investment()
        # update the bank's reserves and the amount it can loan right now
        self.bank.bank_balance()
