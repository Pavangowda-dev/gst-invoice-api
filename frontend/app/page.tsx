"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const STATES: [string, string][] = [
  ["01", "Jammu and Kashmir"], ["02", "Himachal Pradesh"], ["03", "Punjab"],
  ["04", "Chandigarh"], ["05", "Uttarakhand"], ["06", "Haryana"], ["07", "Delhi"],
  ["08", "Rajasthan"], ["09", "Uttar Pradesh"], ["10", "Bihar"], ["11", "Sikkim"],
  ["12", "Arunachal Pradesh"], ["13", "Nagaland"], ["14", "Manipur"],
  ["15", "Mizoram"], ["16", "Tripura"], ["17", "Meghalaya"], ["18", "Assam"],
  ["19", "West Bengal"], ["20", "Jharkhand"], ["21", "Odisha"],
  ["22", "Chhattisgarh"], ["23", "Madhya Pradesh"], ["24", "Gujarat"],
  ["25", "Daman and Diu"], ["26", "Dadra and Nagar Haveli and Daman and Diu"],
  ["27", "Maharashtra"], ["29", "Karnataka"], ["30", "Goa"], ["31", "Lakshadweep"],
  ["32", "Kerala"], ["33", "Tamil Nadu"], ["34", "Puducherry"],
  ["35", "Andaman and Nicobar Islands"], ["36", "Telangana"],
  ["37", "Andhra Pradesh"], ["38", "Ladakh"],
];

const GST_RATES = ["0", "0.25", "3", "5", "18", "40"];

type Party = {
  name: string;
  gstin: string;
  line1: string;
  city: string;
  stateCode: string;
  pincode: string;
};

type Item = {
  description: string;
  hsn: string;
  quantity: string;
  unitPrice: string;
  gstRate: string;
  discount: string;
};

type Bank = {
  accountName: string;
  bankName: string;
  accountNumber: string;
  ifsc: string;
  upiId: string;
};

type Preview = {
  tax_type: "intra_state" | "inter_state";
  totals: {
    discount: string;
    taxable_value: string;
    cgst: string;
    sgst: string;
    igst: string;
    round_off: string;
    grand_total: string;
  };
};

const emptyParty: Party = { name: "", gstin: "", line1: "", city: "", stateCode: "", pincode: "" };
const emptyItem: Item = { description: "", hsn: "", quantity: "1", unitPrice: "", gstRate: "18", discount: "" };
const emptyBank: Bank = { accountName: "", bankName: "", accountNumber: "", ifsc: "", upiId: "" };

function toParty(p: Party) {
  return {
    name: p.name.trim(),
    gstin: p.gstin.trim() || null,
    address: {
      line1: p.line1.trim(),
      city: p.city.trim(),
      state_code: p.stateCode,
      pincode: p.pincode.trim(),
    },
  };
}

// bank details are optional: if the person left everything empty, send nothing
function toBank(b: Bank) {
  const filled = [b.accountName, b.bankName, b.accountNumber, b.ifsc, b.upiId].some((v) => v.trim());
  if (!filled) return null;
  return {
    account_name: b.accountName.trim(),
    bank_name: b.bankName.trim(),
    account_number: b.accountNumber.trim(),
    ifsc: b.ifsc.trim(),
    upi_id: b.upiId.trim() || null,
  };
}

function buildPayload(seller: Party, buyer: Party, number: string, date: string, notes: string, items: Item[], bank: Bank) {
  return {
    invoice_number: number.trim(),
    invoice_date: date || undefined,
    seller: toParty(seller),
    buyer: toParty(buyer),
    bank_details: toBank(bank),
    notes: notes.trim() || null,
    items: items.map((i) => ({
      description: i.description.trim(),
      hsn_sac: i.hsn.trim(),
      quantity: i.quantity,
      unit_price: i.unitPrice,
      gst_rate: i.gstRate,
      discount_percent: i.discount || "0",
    })),
  };
}

// FastAPI sends validation problems as a list; turn them into readable lines
function readErrors(data: any): string[] {
  if (!Array.isArray(data?.detail)) return ["Something went wrong. Please check the form."];
  return data.detail.map((d: any) => {
    const where = (d.loc ?? []).slice(1).join(" → ");
    const message = String(d.msg).replace("Value error, ", "");
    return where ? `${where}: ${message}` : message;
  });
}

function money(value: string) {
  return Number(value).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

const inputClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-600">{label}</span>
      {children}
    </label>
  );
}

function TextInput(props: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  maxLength?: number;
  type?: string;
}) {
  return (
    <Field label={props.label}>
      <input
        className={inputClass}
        type={props.type ?? "text"}
        value={props.value}
        maxLength={props.maxLength}
        placeholder={props.placeholder}
        onChange={(e) => props.onChange(e.target.value)}
      />
    </Field>
  );
}

function Card({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-slate-900">{title}</h2>
      {hint && <p className="mb-4 mt-0.5 text-xs text-slate-500">{hint}</p>}
      {!hint && <div className="mb-4" />}
      {children}
    </section>
  );
}

function PartyForm({ party, onChange, gstinLabel }: { party: Party; onChange: (p: Party) => void; gstinLabel: string }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <TextInput label="Name" value={party.name} onChange={(v) => onChange({ ...party, name: v })} />
      <TextInput label={gstinLabel} value={party.gstin} maxLength={15} placeholder="15 characters" onChange={(v) => onChange({ ...party, gstin: v.toUpperCase() })} />
      <div className="sm:col-span-2">
        <TextInput label="Address" value={party.line1} onChange={(v) => onChange({ ...party, line1: v })} />
      </div>
      <TextInput label="City" value={party.city} onChange={(v) => onChange({ ...party, city: v })} />
      <TextInput label="Pincode" value={party.pincode} maxLength={6} onChange={(v) => onChange({ ...party, pincode: v.replace(/\D/g, "") })} />
      <div className="sm:col-span-2">
        <Field label="State">
          <select className={inputClass} value={party.stateCode} onChange={(e) => onChange({ ...party, stateCode: e.target.value })}>
            <option value="">Select state</option>
            {STATES.map(([code, name]) => (
              <option key={code} value={code}>
                {name} ({code})
              </option>
            ))}
          </select>
        </Field>
      </div>
    </div>
  );
}

export default function Home() {
  const [seller, setSeller] = useState<Party>(emptyParty);
  const [buyer, setBuyer] = useState<Party>(emptyParty);
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [invoiceDate, setInvoiceDate] = useState("");
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState<Item[]>([{ ...emptyItem }]);
  const [bank, setBank] = useState<Bank>(emptyBank);

  const [preview, setPreview] = useState<Preview | null>(null);
  const [offline, setOffline] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [downloading, setDownloading] = useState(false);

  // set the date after mount so server and browser never disagree about "today"
  useEffect(() => {
    setInvoiceDate(new Date().toLocaleDateString("en-CA"));
  }, []);

  const body = JSON.stringify(buildPayload(seller, buyer, invoiceNumber, invoiceDate, notes, items, bank));

  // live totals: ask the API to calculate whenever the form changes
  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API_URL}/invoices/calculate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
        });
        setOffline(false);
        setPreview(res.ok ? await res.json() : null);
      } catch {
        setOffline(true);
        setPreview(null);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [body]);

  function updateItem(index: number, changes: Partial<Item>) {
    setItems(items.map((item, i) => (i === index ? { ...item, ...changes } : item)));
  }

  function fillSample() {
    setSeller({ name: "Test Seller", gstin: "29ABCDE1234F1ZW", line1: "12 MG Road", city: "Bengaluru", stateCode: "29", pincode: "560001" });
    setBuyer({ name: "Test Buyer", gstin: "33AAACR1234A1ZA", line1: "45 Anna Salai", city: "Chennai", stateCode: "33", pincode: "600002" });
    setInvoiceNumber("INV-001");
    setNotes("Thank you for your business. Payment due within 7 days.");
    setItems([
      { description: "Website development", hsn: "998314", quantity: "1", unitPrice: "50000", gstRate: "18", discount: "10" },
      { description: "Hosting and maintenance (1 year)", hsn: "998315", quantity: "1", unitPrice: "12000", gstRate: "18", discount: "" },
    ]);
    setBank({ accountName: "Test Seller", bankName: "Test Bank", accountNumber: "50100123456789", ifsc: "TEST0001234", upiId: "testseller@testbank" });
  }

  async function downloadPdf() {
    setErrors([]);
    setDownloading(true);
    try {
      const res = await fetch(`${API_URL}/invoices/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      if (!res.ok) {
        setErrors(readErrors(await res.json()));
        return;
      }
      const url = URL.createObjectURL(await res.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = `invoice-${invoiceNumber.replace(/[^A-Za-z0-9_-]/g, "-") || "draft"}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setErrors([`Could not reach the API at ${API_URL}. Is the backend running?`]);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-8 text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">GST Invoice Generator</h1>
            <p className="mt-1 text-sm text-indigo-100">Fill in the details, check the tax, and download a ready PDF invoice.</p>
          </div>
          <button onClick={fillSample} className="rounded-lg bg-white/15 px-4 py-2 text-sm font-medium hover:bg-white/25">
            Fill sample data
          </button>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card title="Invoice details">
            <div className="grid gap-3 sm:grid-cols-2">
              <TextInput label="Invoice number" value={invoiceNumber} maxLength={16} placeholder="INV-001" onChange={setInvoiceNumber} />
              <TextInput label="Invoice date" type="date" value={invoiceDate} onChange={setInvoiceDate} />
            </div>
          </Card>

          <Card title="Seller (you)" hint="GSTIN is required on a tax invoice and is checked for typos.">
            <PartyForm party={seller} onChange={setSeller} gstinLabel="GSTIN" />
          </Card>

          <Card title="Buyer" hint="Leave GSTIN empty if the buyer is not registered for GST.">
            <PartyForm party={buyer} onChange={setBuyer} gstinLabel="GSTIN (optional)" />
          </Card>

          <Card title="Items" hint="Use the HSN code for goods and the SAC code for services. GST is charged after the discount.">
            <div className="space-y-4">
              {items.map((item, index) => (
                <div key={index} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="grid gap-3 sm:grid-cols-12">
                    <div className="sm:col-span-8">
                      <TextInput label="Description" value={item.description} onChange={(v) => updateItem(index, { description: v })} />
                    </div>
                    <div className="sm:col-span-4">
                      <TextInput label="HSN / SAC" value={item.hsn} maxLength={8} placeholder="998314" onChange={(v) => updateItem(index, { hsn: v.replace(/\D/g, "") })} />
                    </div>
                    <div className="sm:col-span-3">
                      <TextInput label="Quantity" type="number" value={item.quantity} onChange={(v) => updateItem(index, { quantity: v })} />
                    </div>
                    <div className="sm:col-span-3">
                      <TextInput label="Price per unit (Rs.)" type="number" value={item.unitPrice} onChange={(v) => updateItem(index, { unitPrice: v })} />
                    </div>
                    <div className="sm:col-span-3">
                      <TextInput label="Discount (%)" type="number" value={item.discount} placeholder="0" onChange={(v) => updateItem(index, { discount: v })} />
                    </div>
                    <div className="sm:col-span-3">
                      <Field label="GST rate">
                        <select className={inputClass} value={item.gstRate} onChange={(e) => updateItem(index, { gstRate: e.target.value })}>
                          {GST_RATES.map((rate) => (
                            <option key={rate} value={rate}>
                              {rate}%
                            </option>
                          ))}
                        </select>
                      </Field>
                    </div>
                  </div>
                  {items.length > 1 && (
                    <button onClick={() => setItems(items.filter((_, i) => i !== index))} className="mt-3 text-xs font-medium text-red-600 hover:underline">
                      Remove item
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button onClick={() => setItems([...items, { ...emptyItem }])} className="mt-4 rounded-lg border border-dashed border-indigo-400 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50">
              + Add another item
            </button>
          </Card>

          <Card title="Bank details (optional)" hint="Printed on the invoice so your client knows where to pay.">
            <div className="grid gap-3 sm:grid-cols-2">
              <TextInput label="Account holder name" value={bank.accountName} onChange={(v) => setBank({ ...bank, accountName: v })} />
              <TextInput label="Bank name" value={bank.bankName} onChange={(v) => setBank({ ...bank, bankName: v })} />
              <TextInput label="Account number" value={bank.accountNumber} maxLength={18} onChange={(v) => setBank({ ...bank, accountNumber: v.replace(/\D/g, "") })} />
              <TextInput label="IFSC code" value={bank.ifsc} maxLength={11} placeholder="ABCD0123456" onChange={(v) => setBank({ ...bank, ifsc: v.toUpperCase() })} />
              <div className="sm:col-span-2">
                <TextInput label="UPI ID (optional)" value={bank.upiId} placeholder="name@bank" onChange={(v) => setBank({ ...bank, upiId: v })} />
              </div>
            </div>
          </Card>

          <Card title="Notes (optional)">
            <textarea className={inputClass} rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Payment terms, thank you note..." />
          </Card>
        </div>

        <aside className="lg:col-span-1">
          <div className="space-y-4 lg:sticky lg:top-6">
            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-base font-semibold">Summary</h2>

              {offline && (
                <p className="mt-3 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
                  Cannot reach the API. Start the backend with uvicorn on {API_URL}.
                </p>
              )}

              {!offline && !preview && (
                <p className="mt-3 text-sm text-slate-500">Complete the form and your tax summary will appear here.</p>
              )}

              {preview && (
                <div className="mt-3 text-sm">
                  <span className="inline-block rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
                    {preview.tax_type === "intra_state" ? "Same state: CGST + SGST" : "Different state: IGST"}
                  </span>
                  <dl className="mt-4 space-y-2">
                    {Number(preview.totals.discount) !== 0 && (
                      <div className="flex justify-between"><dt className="text-slate-600">Total discount</dt><dd>- {money(preview.totals.discount)}</dd></div>
                    )}
                    <div className="flex justify-between"><dt className="text-slate-600">Taxable value</dt><dd>{money(preview.totals.taxable_value)}</dd></div>
                    {preview.tax_type === "intra_state" ? (
                      <>
                        <div className="flex justify-between"><dt className="text-slate-600">CGST</dt><dd>{money(preview.totals.cgst)}</dd></div>
                        <div className="flex justify-between"><dt className="text-slate-600">SGST</dt><dd>{money(preview.totals.sgst)}</dd></div>
                      </>
                    ) : (
                      <div className="flex justify-between"><dt className="text-slate-600">IGST</dt><dd>{money(preview.totals.igst)}</dd></div>
                    )}
                    {Number(preview.totals.round_off) !== 0 && (
                      <div className="flex justify-between"><dt className="text-slate-600">Round off</dt><dd>{money(preview.totals.round_off)}</dd></div>
                    )}
                    <div className="flex justify-between border-t border-slate-200 pt-3 text-base font-semibold">
                      <dt>Grand total</dt><dd>Rs. {money(preview.totals.grand_total)}</dd>
                    </div>
                  </dl>
                </div>
              )}
            </section>

            <button
              onClick={downloadPdf}
              disabled={downloading}
              className="w-full rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-60"
            >
              {downloading ? "Creating PDF..." : "Download PDF invoice"}
            </button>

            {errors.length > 0 && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-800">
                <p className="mb-1 font-semibold">Please fix these:</p>
                <ul className="list-disc space-y-1 pl-4">
                  {errors.map((message, i) => (
                    <li key={i}>{message}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}