"use client";

import { useState, useEffect } from "react";

export interface BusinessConfig {
  business: {
    name: string;
    tagline: string;
    ai_name: string;
    ai_role: string;
    currency: string;
    tax_rate: number;
    tax_label: string;
  };
  contact: {
    whatsapp: string;
    website: string;
    email: string;
    phone: string;
    address: string;
  };
  bank_account: {
    bank: string;
    number: string;
    name: string;
    label: string;
  };
  brands: string[];
  proposal: {
    letter_number_prefix: string;
    letter_number_suffix: string;
    company_city: string;
    signatory: string;
    signatory_title: string;
    terms: string[];
  };
  project_types: {
    id: string;
    label: string;
    keywords: string[];
    installation_fee: number;
  }[];
  system_types: {
    id: string;
    label: string;
    has_hdd: boolean;
    has_nvr: boolean;
    has_poe_switch: boolean;
    has_utp_cable: boolean;
    has_coaxial_cable: boolean;
    has_power_cable: boolean;
    has_sd_card: boolean;
    catalog_camera_type: string;
  }[];
  cable_prices: {
    utp: { label: string; price_per_meter: number; auto_per_camera: number };
    power: { label: string; price_per_meter: number };
    coaxial: { label: string; price_per_meter: number };
    conduit: { label: string; price_per_unit: number; meter_per_unit: number };
  };
  resolutions: string[];
  sd_card_options: { size_gb: number; label: string; price: number }[];
  surat_penawaran: {
    show_logo: boolean;
    show_bank_account: boolean;
    show_ttd: boolean;
  };
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

let cachedConfig: BusinessConfig | null = null;
let configPromise: Promise<BusinessConfig> | null = null;

function fetchConfig(): Promise<BusinessConfig> {
  if (cachedConfig) return Promise.resolve(cachedConfig);
  if (configPromise) return configPromise;
  configPromise = fetch(`${API_BASE}/config`)
    .then((res) => res.json())
    .then((data) => {
      cachedConfig = data;
      return data as BusinessConfig;
    });
  return configPromise;
}

export function useBusinessConfig() {
  const [config, setConfig] = useState<BusinessConfig | null>(cachedConfig);
  const [loading, setLoading] = useState(!cachedConfig);

  useEffect(() => {
    if (cachedConfig) {
      setConfig(cachedConfig);
      setLoading(false);
      return;
    }
    fetchConfig().then((data) => {
      setConfig(data);
      setLoading(false);
    });
  }, []);

  return { config, loading };
}

export { fetchConfig };
