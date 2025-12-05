
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
from datetime import datetime
from collections import deque
import xml.etree.ElementTree as ET
import xml.dom.minidom
import copy
import os

class SloTaxApp:
    """
    SloTax ETF Manager
    A desktop application to manage stock/ETF transactions, calculate capital gains
    tax based on Slovenian FIFO rules, and export for eDavki.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("SloTax ETF Manager")
        self.root.geometry("1200x600")

        # Data storage
        self.transactions = []
        self.portfolio_file = "portfolio.json"

        self.create_widgets()
        self.load_transactions()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Left Panel (Input) ---
        left_panel = ttk.LabelFrame(main_frame, text="Vnos Transakcije", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_panel, text="Datum (DD.MM.YYYY):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_entry = ttk.Entry(left_panel)
        self.date_entry.grid(row=0, column=1, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))

        ttk.Label(left_panel, text="Tip:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.type_combo = ttk.Combobox(left_panel, values=["Nakup", "Prodaja"], state="readonly")
        self.type_combo.grid(row=1, column=1, pady=2)
        self.type_combo.set("Nakup")

        ttk.Label(left_panel, text="Ticker:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ticker_entry = ttk.Entry(left_panel)
        self.ticker_entry.grid(row=2, column=1, pady=2)

        ttk.Label(left_panel, text="Količina:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.quantity_entry = ttk.Entry(left_panel)
        self.quantity_entry.grid(row=3, column=1, pady=2)

        ttk.Label(left_panel, text="Cena na enoto (€):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.price_entry = ttk.Entry(left_panel)
        self.price_entry.grid(row=4, column=1, pady=2)
        
        ttk.Label(left_panel, text="Stroški (€):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.costs_entry = ttk.Entry(left_panel)
        self.costs_entry.grid(row=5, column=1, pady=2)
        self.costs_entry.insert(0, "0.0")

        add_button = ttk.Button(left_panel, text="Dodaj Transakcijo", command=self.add_transaction)
        add_button.grid(row=6, columnspan=2, pady=20, sticky="ew")

        # --- Right Panel (View) ---
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tree_frame = ttk.Frame(right_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("date", "type", "ticker", "quantity", "price", "costs", "total_value")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Datum")
        self.tree.heading("type", text="Tip")
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("quantity", text="Količina")
        self.tree.heading("price", text="Cena/enoto")
        self.tree.heading("costs", text="Stroški")
        self.tree.heading("total_value", text="Skupna Vrednost (€)")

        self.tree.column("date", width=100, anchor=tk.W)
        self.tree.column("type", width=80, anchor=tk.W)
        self.tree.column("ticker", width=100, anchor=tk.W)
        self.tree.column("quantity", width=100, anchor=tk.E)
        self.tree.column("price", width=100, anchor=tk.E)
        self.tree.column("costs", width=80, anchor=tk.E)
        self.tree.column("total_value", width=150, anchor=tk.E)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        delete_button = ttk.Button(right_panel, text="Zbriši Izbrano", command=self.delete_transaction)
        delete_button.pack(pady=5, fill=tk.X)

        # --- Bottom Panel (Actions & Status Bar) ---
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        action_panel = ttk.Frame(bottom_frame)
        action_panel.pack(side=tk.TOP, fill=tk.X, expand=True)

        export_csv_button = ttk.Button(action_panel, text="Izvozi CSV", command=self.export_to_csv)
        export_csv_button.pack(side=tk.LEFT, padx=5)

        generate_xml_button = ttk.Button(action_panel, text="Ustvari XML za eDavke", command=self.generate_edavki_xml)
        generate_xml_button.pack(side=tk.LEFT, padx=5)

        self.status_bar = tk.Label(bottom_frame, text="Pripravljen.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=True, ipady=2)

    def update_status(self, message, is_error=False):
        self.status_bar.config(text=message, fg="red" if is_error else "black")

    def load_transactions(self):
        """
        Loads transactions from the portfolio.json file upon startup.
        If the file doesn't exist, it does nothing and waits for new transactions.
        If the file is corrupted, it shows an error.
        """
        if not os.path.exists(self.portfolio_file):
            self.update_status(f"Datoteka '{self.portfolio_file}' ne obstaja. Ustvarjena bo ob prvem shranjevanju.")
            return

        try:
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                self.transactions = json.load(f)
            self.populate_treeview()
            self.update_status(f"Transakcije uspešno naložene iz '{self.portfolio_file}'.")
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showerror("Napaka pri nalaganju", f"Datoteko '{self.portfolio_file}' je poškodovana ali je ni mogoče prebrati.")
            self.update_status("Napaka pri nalaganju transakcij.", is_error=True)

    def save_transactions(self):
        """
        Saves the current list of transactions to the portfolio.json file.
        This function is called every time a transaction is added or deleted,
        ensuring data persistence. The JSON format is human-readable and easy
        to back up. Data is saved with an indent for better readability.
        """
        try:
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(self.transactions, f, indent=4, ensure_ascii=False)
            self.update_status("Transakcije shranjene.")
        except IOError:
            messagebox.showerror("Napaka pri shranjevanju", f"Datoteke '{self.portfolio_file}' ni mogoče zapisati.")
            self.update_status("Napaka pri shranjevanju transakcij.", is_error=True)

    def populate_treeview(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sort by date before populating
        sorted_transactions = sorted(self.transactions, key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y"))
        
        # Add new items
        for tx in sorted_transactions:
            total_value = tx['quantity'] * tx['price']
            self.tree.insert("", tk.END, values=(
                tx['date'],
                tx['type'],
                tx['ticker'],
                f"{tx['quantity']:.4f}",
                f"{tx['price']:.4f}",
                f"{tx['costs']:.4f}",
                f"{total_value:.2f}"
            ))

    def add_transaction(self):
        # --- 1. Get and Validate Inputs ---
        date_str = self.date_entry.get().strip()
        tx_type = self.type_combo.get()
        ticker = self.ticker_entry.get().strip().upper()
        
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            self.update_status("Napaka: Neveljaven format datuma. Uporabite DD.MM.YYYY.", is_error=True)
            return

        if not ticker:
            self.update_status("Napaka: Ticker ne sme biti prazen.", is_error=True)
            return
            
        try:
            quantity = float(self.quantity_entry.get().replace(',', '.'))
            price = float(self.price_entry.get().replace(',', '.'))
            costs = float(self.costs_entry.get().replace(',', '.'))
        except ValueError:
            self.update_status("Napaka: Količina, cena in stroški morajo biti številske vrednosti.", is_error=True)
            return

        # --- 2. Create Transaction Dictionary ---
        new_tx = {
            "date": date_str,
            "type": tx_type,
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "costs": costs
        }

        # --- 3. Update Data and UI ---
        self.transactions.append(new_tx)
        self.save_transactions()
        self.populate_treeview()

        # --- 4. Clear Entry Fields ---
        self.ticker_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.costs_entry.delete(0, tk.END)
        self.costs_entry.insert(0, "0.0")
        self.ticker_entry.focus()
        self.update_status("Transakcija uspešno dodana.")

    def delete_transaction(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.update_status("Nobena transakcija ni izbrana za brisanje.", is_error=True)
            return

        if messagebox.askyesno("Potrdi Brisanje", "Ali ste prepričani, da želite zbrisati izbrane transakcije?"):
            # We need to delete from the bottom up to not mess up indices
            # The Treeview selection gives us item IDs, which we can map to our list
            
            # Create a map of treeview item values (as a tuple) to its index in the original list
            sorted_trans = sorted(self.transactions, key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y"))
            
            items_to_delete_indices = []
            for item_id in selected_items:
                item_values = self.tree.item(item_id)['values']
                # Find this item in our sorted transaction list to find its original counterpart
                for i, tx in enumerate(sorted_trans):
                     total_value = tx['quantity'] * tx['price']
                     tree_values = (
                         tx['date'], tx['type'], tx['ticker'], f"{tx['quantity']:.4f}",
                         f"{tx['price']:.4f}", f"{tx['costs']:.4f}", f"{total_value:.2f}"
                     )
                     if tuple(map(str, tree_values)) == tuple(map(str, item_values)):
                         # Now find this tx in the original self.transactions list by object identity
                         original_index = -1
                         for j, original_tx in enumerate(self.transactions):
                             if original_tx is tx:
                                 original_index = j
                                 break
                         if original_index != -1:
                            items_to_delete_indices.append(original_index)
                         break

            # Delete from the original list using indices, sorted descending to avoid index shifting issues
            for index in sorted(items_to_delete_indices, reverse=True):
                del self.transactions[index]

            self.save_transactions()
            self.populate_treeview()
            self.update_status("Izbrane transakcije so bile zbrisane.")


    def export_to_csv(self):
        if not self.transactions:
            self.update_status("Ni transakcij za izvoz.", is_error=True)
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV datoteke", "*.csv"), ("Vse datoteke", "*.*")],
            title="Izvozi kot CSV"
        )
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.transactions[0].keys())
                writer.writeheader()
                writer.writerows(self.transactions)
            self.update_status(f"Podatki uspešno izvoženi v '{filename}'.")
        except IOError:
            messagebox.showerror("Napaka pri izvozu", f"Datoteke '{filename}' ni mogoče zapisati.")
            self.update_status("Napaka pri izvozu v CSV.", is_error=True)

    def generate_edavki_xml(self):
        """
        Main logic for FIFO calculation and XML generation.
        """
        # --- 1. Group transactions by ticker ---
        transactions_by_ticker = {}
        for tx in self.transactions:
            ticker = tx['ticker']
            if ticker not in transactions_by_ticker:
                transactions_by_ticker[ticker] = []
            transactions_by_ticker[ticker].append(tx)

        # This list will hold all the matched sale-purchase pairs for XML generation.
        all_matched_pairs = []
        
        # --- 2. Process each ticker group with FIFO logic ---
        for ticker, tx_list in transactions_by_ticker.items():
            
            # Sort by date to ensure correct FIFO order
            tx_list.sort(key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y"))

            # Separate buys and sells. We use deepcopy to avoid modifying the original data.
            # We add a 'remaining_quantity' key to buys to track partially used lots.
            buys = deque()
            for tx in tx_list:
                if tx['type'] == 'Nakup':
                    buy_copy = copy.deepcopy(tx)
                    buy_copy['remaining_quantity'] = buy_copy['quantity']
                    buys.append(buy_copy)
            
            sells = [tx for tx in tx_list if tx['type'] == 'Prodaja']

            if not sells:
                continue # No sales for this ticker, nothing to do.

            # --- FIFO Engine Core Logic ---
            # For each sale, find the corresponding purchase(s) on a first-in, first-out basis.
            for sale in sells:
                quantity_to_sell = sale['quantity']
                
                # Keep matching with the oldest buys until the sale quantity is fully covered
                while quantity_to_sell > 1e-9: # Use a small epsilon for float comparison
                    if not buys:
                        messagebox.showerror("Napaka v logiki", f"Ni dovolj nakupov za kritje prodaje {sale['quantity']} enot {ticker} na dan {sale['date']}.")
                        self.update_status("Napaka: Prodaja brez ustreznega nakupa.", is_error=True)
                        return
                    
                    oldest_buy = buys[0]
                    
                    # Determine the amount to match in this iteration
                    match_quantity = min(quantity_to_sell, oldest_buy['remaining_quantity'])
                    
                    # Store the matched pair (sale, buy, matched_quantity) for XML generation
                    all_matched_pairs.append({
                        "sale": sale,
                        "buy": oldest_buy,
                        "quantity": match_quantity
                    })
                    
                    # Update remaining quantities
                    oldest_buy['remaining_quantity'] -= match_quantity
                    quantity_to_sell -= match_quantity

                    # If the oldest buy is fully used up, remove it from the deque
                    if oldest_buy['remaining_quantity'] < 1e-9:
                        buys.popleft()

        if not all_matched_pairs:
            self.update_status("Ni prodaj za poročanje v tekočem letu.", is_error=False)
            messagebox.showinfo("Info", "Ni relevantnih prodaj za izvoz v XML.")
            return

        # --- 3. Build the XML structure ---
        self._create_xml_file(all_matched_pairs)

    def _create_xml_file(self, matched_pairs):
        # Create root element with namespaces
        envelope = ET.Element("Envelope", {
            "xmlns": "http://edavki.durs.si/Documents/Schemas/Doh_KDVP_9.xsd",
            "xmlns:edp": "http://edavki.durs.si/Documents/Schemas/Edp-Common-1.xsd"
        })
        body = ET.SubElement(envelope, "body")
        doh_kdvp = ET.SubElement(body, "Doh_KDVP", {"Leto": str(datetime.now().year -1)})
        # Assuming the tax form is for the previous year. 
        # User should be mindful of the transaction dates they input.

        # Create an item for each matched pair
        for pair in matched_pairs:
            sale = pair['sale']
            buy = pair['buy']
            qty = pair['quantity']

            # Calculate values for this specific matched quantity
            sale_price_per_unit = sale['price']
            buy_price_per_unit = buy['price']

            # Apportion costs based on the quantity being sold
            # Sale costs are apportioned from the total sale transaction costs
            prorated_sale_costs = (sale['costs'] / sale['quantity']) * qty if sale['quantity'] > 0 else 0
            # Buy costs are apportioned from the total buy transaction costs
            prorated_buy_costs = (buy['costs'] / buy['quantity']) * qty if buy['quantity'] > 0 else 0
            
            # Per eDavki schema:
            # Vrednost ob pridobitvi = (Nakupna cena * Količina) + Stroški nakupa
            # Vrednost ob odsvojitvi = (Prodajna cena * Količina) - Stroški prodaje
            vrednost_pridobitev = (buy_price_per_unit * qty) + prorated_buy_costs
            vrednost_odsvojitev = (sale_price_per_unit * qty) - prorated_sale_costs

            item = ET.SubElement(doh_kdvp, "KDVP")

            # --- Section A: Podatki o zavezancu ---
            # This section is typically filled out manually or by the eDavki system.
            # We are focusing on the capital gains items.
            
            # --- Section 6: Podatki o doseženih dobičkih in izgubah... ---
            item.set("Oznaka", "61") # Oznaka za Vrednostne papirje in deleže

            # Podatki o odsvojitvi (Sale)
            odsvojitev = ET.SubElement(item, "Odsvojitev")
            ET.SubElement(odsvojitev, "DatumOdsvojitve").text = sale['date']
            ET.SubElement(odsvojitev, "VrednostOdsvojitve").text = f"{vrednost_odsvojitev:.4f}"
            ET.SubElement(odsvojitev, "SteviloEnot").text = f"{qty:.4f}"
            
            # Podatki o pridobitvi (Buy)
            pridobitev = ET.SubElement(item, "Pridobitev")
            ET.SubElement(pridobitev, "DatumPridobitve").text = buy['date']
            ET.SubElement(pridobitev, "VrednostPridobitve").text = f"{vrednost_pridobitev:.4f}"
            ET.SubElement(pridobitev, "NacinPridobitve").text = "A" # A = Nakup
            ET.SubElement(pridobitev, "SteviloEnot").text = f"{qty:.4f}"
            
        # --- 4. Write to file ---
        xml_str = ET.tostring(envelope, 'utf-8')
        
        # Pretty print
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml_str = dom.toprettyxml(indent="  ", encoding="utf-8")

        filename = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML datoteke", "*.xml"), ("Vse datoteke", "*.*")],
            title="Shrani eDavki XML",
            initialfile="Doh-KDVP.xml"
        )
        if not filename:
            return

        try:
            with open(filename, 'wb') as f:
                f.write(pretty_xml_str)
            self.update_status(f"XML datoteka za eDavke uspešno ustvarjena v '{filename}'.")
            messagebox.showinfo("Uspeh", f"XML datoteka '{filename}' je bila uspešno ustvarjena.")
        except IOError:
            messagebox.showerror("Napaka pri shranjevanju", f"Datoteke '{filename}' ni mogoče zapisati.")
            self.update_status("Napaka pri ustvarjanju XML datoteke.", is_error=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SloTaxApp(root)
    root.mainloop()
