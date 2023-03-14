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
import numpy as np

from bank_asset.random_walk import RandomWalker

'''simple bank will set a single interest rate such that cash flow is balanced. simple bank cannot directly invest in risky assets'''
class Bank(mesa.Agent):
    def __init__(self, unique_id, model, reserve_percent=50, 
                 deposit_interest=1, loan_interest=2, risk_preference=0.5, haircut = 0.5, p_asset0 = 10, cash = 2000):
        # initialize the parent class with required parameters
        super().__init__(unique_id, model)

        '''properties'''

        # for tracking total value of loans outstanding
        self.loans = 0
        #percent of deposits the bank must keep in reserves - this is set via Slider in server.py
        self.reserve_percent = reserve_percent
        # for tracking total value of deposits
        self.deposits = 0
        # amount the bank is currently able to loan
        self.bank_to_loan = 0
        # haircut that bank uses to calculate collateral
        self.haircut = haircut
        # number of liquidity crisis that this bank has incurred
        self.l_crisis = 0
        # amount of cash the bank holds
        self.cash = cash
        # interest rate of their loan
        self.loan_interest = loan_interest
        # interest payment rate to their customers
        self.deposit_interest = deposit_interest
        # assets -- for tracking consumption
        self.asset0_consumed = 0
        # # minimum deposit interest
        # self.min_deposit_interest = 

    '''adjust interest rates so that cash flow is balanced'''
    def adjust_rates(self):
        # assumptions: 1) loan interest must be at least fed interest, otherwise no incentive to give loans 2) deposit - loan interest diff must be such that bank is not losing money
        self.loan_interest = self.model.fed_interest
        loan_rev = self.loans * self.loan_interest/100
        # to_shrink = self.
        self.deposit_interest = loan_rev/ self.deposits



        # assumptions: 1) deposit interest must be at least fed interest, otherwise no incentive to give put deposit in bank 2) deposit - loan interest diff must be such that bank is not losing money
        # self.deposit_interest = self.model.fed_interest
        # deposit_costs = self.deposits * self.deposit_interest/100
        # self.loan_interest = deposit_costs/self.loans
        # print('bank c', self.cash)
        print('bank di', self.deposit_interest)

    # '''calculate the loan interest rate this period'''
    # def calculate_loan_rate(self):
    #     pass

    # '''calculate the deposit interest rate this period'''
    # def calculate_deposit_rate(self):
    #     pass

    '''calculate total amount of required reserves'''
    def req_reserves(self, deposits = None):
        if deposits is None:
            return (self.reserve_percent / 100) * self.deposits
        else:
            return (self.reserve_percent / 100) * deposits
    
    '''check if bank meets reserve requirements'''
    def check_reserves(self):
        if self.req_reserves() > self.cash:
            # self.l_crisis += 1
            pass

    '''withdraws some amount of cash from bank. returns whether it happened'''
    def withdraw(self, amount):
        if self.cash - amount >= self.req_reserves(self.deposits - amount):
            self.cash -= amount
            self.deposits -= amount
            return True
        else:
            self.l_crisis += 1
            return False

    def deposit(self, amount):
        self.deposits += amount
        self.cash += amount
        return True

    def give_loan(self, amount):
        if self.cash - amount >= self.req_reserves():
            self.cash -= amount
            self.loans += amount
            return True
        else:
            self.l_crisis += 1
            return False

    def pay_loan(self, amount):
        self.loans -= amount
        self.cash += amount
        return True

   # total balance of firm's deposits/loans in bank. Can be negative

'''simple firm will try to invest in the most profitable asset. will also try to keep some cash availiable'''
class Firm(RandomWalker):
    def __init__(self, unique_id, pos, model, moore, bank: Bank, leverage = 2, asset = 10, cash = 10, savings = 90, productivity=None, p_asset0 = 10, prod_variance = 0.5, prod_drift_V = 0.1, discount_rate = 0.05, deathrate=0.05):
        # init parent class with required parameters
        super().__init__(unique_id, pos, model, moore=moore)
        '''default options'''
        if productivity is None:
            productivity = max(-prod_variance/2,-0.1)

        '''
        properties
        '''
        # person's bank, set at __init__
        self.bank = bank
        # the amount each firm has in physical cash. Must be positive
        self.cash = cash
        # amount of deposits in bank
        self.savings = savings
        self.bank.deposits += savings
        # amount of loans from bank
        self.loans = 0
        # the amount each firm has in asset 0. Must be positive
        self.asset0 = asset
        # the percentage increase in assets this firm can create in each period
        self.productivity = productivity
        # how much leverage this firm seeks (ie. loan to collateral ratio)
        self.leverage = leverage
        # whether this firm is bankrupt or not
        self.bankrupt = False
        # the value that the firm places on asset0
        self.p_asset0 = p_asset0
        # firms will try to hold some amount of cash for trading
        self.prod_variance = prod_variance
        # how much the firm's productivity can change by each period
        self.prod_drift_V = prod_drift_V
        # assets not used for production currently
        self.asset0_storage = 0
        # discount rate
        self.discount_rate = discount_rate
        # probability of dying each turn
        self.deathrate = deathrate

        """start everyone off with a random amount in their wallet from 1 to a
           user settable rich threshold amount"""
        # self.wallet = self.random.randint(1, rich_threshold + 1)
        # # savings minus loans, see balance_books() below
        # self.wealth = 0

    def get_neighbors(self):
        return self.model.grid.get_neighbors(self.pos, self.moore, True)

    def buy_assets(self):
        '''attempt to buy 1 unit of asset0 from the neighbor with the lowest valuation'''
        best_nb = None
        best_nb_p = self.p_asset0
        for nb in self.get_neighbors():
            if nb.p_asset0 < best_nb_p and nb.asset0 >= 1:
                best_nb_p = nb.p_asset0
                best_nb = nb
        if best_nb is not None:
            price = (self.p_asset0 + best_nb_p)/2
        
            # transact
            if self.pay(price):
                self.asset0_storage += 1
                nb.asset0 -= 1
                nb.receive(price)
                self.model.report_p_asset0(price)

    def sell_assets(self, isdesperate=False):
        '''attempt to sell off 1 unit of asset0 to the neighbor with the highest valuation'''
        if self.asset0 >= 1:
            best_nb = None
            best_nb_p = self.p_asset0
            if isdesperate:
                best_nb_p = 0
            for nb in self.get_neighbors():
                if nb.p_asset0 > best_nb_p:
                    best_nb_p = nb.p_asset0
                    best_nb = nb
            if best_nb is not None:
                price = (self.p_asset0 + best_nb_p)/2
            
                # transact
                if nb.pay(price):
                    self.asset0 -= 1
                    nb.asset0_storage += 1
                    self.receive(price)
                    self.model.report_p_asset0(price)
                
    def receive(self, amount):
        self.cash += amount

    def expected_return_asset0(self):
        # geometric expected
        return np.exp(self.productivity + self.prod_variance/2)-1

    def produce(self):
        '''Create value using the assets they have'''
        # geometric production
        self.asset0 *= np.exp(self.random.gauss(self.productivity, self.prod_variance**2))

        # additive production
        # if self.asset0 > 0:
        #     self.asset0 += self.asset0 * self.random.gauss(self.productivity, self.prod_variance)
        #     if self.asset0 < 0:
        #         self.asset0 = 0

        # productivity drifts
        self.productivity += self.random.gauss(0, self.prod_drift_V**2)
        
        
        print('v', self.valuation())
        # print('a', self.asset0)
        # print('s', self.savings)
        print('p', self.p_asset0)
        print('d', self.expected_return_asset0())

        # get rid of small assets
        if self.asset0 < 1:
            self.asset0 = 0
        

    def liquidate(self):
        """If the firm does not have enough collateral to meet bank requirements, they must liquidate (sell) assets each round until they meet requirements. They cannot do anything else"""
        self.sell_assets(isdesperate=True)
        
    def valuation(self):
        return(self.bank.haircut * self.model.p_asset0 * self.asset0 + self.cash - self.loans + self.savings)

    def expected_value(self):
        return(self.asset0*self.model.p_asset0 + self.cash - self.loans + self.savings + (self.model.p_asset0 * self.expected_return_asset0()+self.savings * self.bank.deposit_interest/100)/self.discount_rate)

    def adjust_p_assets(self):
        '''firm simply assumes that 1) all r.v. are indepent and 2) all r.v. have mean equal to present value (are martingales)'''
        # self.p_asset0 = max(0,self.model.p_asset0 + (self.model.p_asset0 * self.expected_return_asset0()-self.bank.deposit_interest/100)/self.discount_rate)
        self.p_asset0 = self.model.p_asset0 * (1+self.expected_return_asset0()) / (1+self.bank.deposit_interest/100)


    def pay(self, amount):
        '''pays amount in cash first. if not enough cash, withdraw cash. if still not enough, take loan. returns whether payment happened'''
        if self.cash >= amount:
            self.cash -= amount
            return True
        else:
            amount1 = amount - self.cash
            if self.savings >= amount1:
                if self.withdraw(amount1):
                    self.cash = 0
                    return True
                else:
                    return False
            else:
                amount2 = amount1 - self.savings
                if self.withdraw(self.savings):
                    if self.take_loan(amount2):
                        self.cash = 0
                        return True
                    else:
                        return False
                else:
                    return False

    def withdraw(self, amount):
        '''withdraw money from savings'''
        if self.bank.withdraw(amount):
            self.savings -= amount
            self.cash += amount
            return True
        else:
            return False
        
    def take_loan(self, amount):
        '''take loan from bank'''
        if self.bank.give_loan(amount):
            self.cash += amount
            self.loans += amount
            return True
        else:
            return False

    def settlement(self):
        if self.savings > 0:
            self.get_interest_payment()
        if self.loans > 0:
            self.pay_interest_payment()

    # part of settlement()
    def get_interest_payment(self):
        """ If i have positive bank deposit, they can get interest payment
        from their bank"""
        interest_payment_from_bank = self.savings * (self.bank.deposit_interest/100)

        # household get money
        self.savings += interest_payment_from_bank
        # total deposit increase
        self.bank.deposits += interest_payment_from_bank
        # check if bank is in liquidity crisis
        self.bank.check_reserves()

    def pay_interest_payment(self):
        """ If i have bank loan, the loan increase bacause the interest payment
        to their bank"""
        interest_payment_to_bank = self.loans * (self.bank.loan_interest/100)
        # get interest payment
        self.loans += interest_payment_to_bank

    def balance_account(self):
        '''Rebalance the firm's investments (assets, cash, loans/deposits)'''
        
        # deposit cash or pay back loans using cash, but try to keep some cash for future use
        amount0 = self.cash - self.p_asset0
        if amount0 > 0:
            # pay loans first
            if self.loans > 0:
                amount1 = min(self.loans, amount0)
                self.loans -= amount1
                amount0 -= amount1
                self.bank.pay_loan(amount1)
            # then deposit
            self.savings += amount0
            self.bank.deposit(amount0)
            self.cash -= amount0

        # put assets to use
        self.asset0 += self.asset0_storage
        self.asset0_storage = 0

    def is_big(self):
        return self.valuation() >= self.model.rich_threshold
    
    def is_small(self):
        return self.valuation() <= self.model.poor_threshold

    def is_bankrupt(self):
        return self.valuation() < 0

    def is_medium(self):
        return not (self.is_big() or self.is_small())

    def is_not_big(self):
        return not (self.is_bankrupt() or self.is_big())

    def is_operating(self):
        return (not self.is_bankrupt()) and self.asset0 >= 1
    
    def is_not_operating(self):
        return (not self.is_bankrupt()) and self.asset0 < 1

    def get_deathrate(self):
        threshold = self.deathrate
        if self.is_bankrupt():
            if self.asset0 <= 0:
                threshold = 1
        else:
            threshold *= np.exp(-self.valuation())
        return threshold

    def check_death(self):
        if self.random.uniform(0,1) < self.get_deathrate():
            # remove the firm
            self.bank.cash += self.cash
            self.bank.loans -= self.loans
            self.bank.deposits -= self.savings
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            

    # step is called for each agent in model.BankReservesModel.schedule.step()
    def step(self):

        # move to a cell in my Moore neighborhood
        self.random_move()

        # settlement their loan and deposit interest payment
        self.settlement()

        # balance investments
        self.balance_account()

        # check if bankrupt. if so, start liquidating
        if self.valuation() < 0:
            self.liquidate()
        # else keep trading/ investing
        else: 
            # buy assets to grow
            self.buy_assets()

            # # sell assets
            # self.sell_assets()

            # produce
            self.produce()

            # check death

        # calibrate valuation
        self.adjust_p_assets()

        # check death
        self.check_death()

