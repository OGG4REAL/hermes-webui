import type { AGUIEvent } from "../agui/aguiReducer";

const customer = {
  id: "cust_001",
  name: "模拟客户",
  risk_level: "R3",
  aum: 3200000,
  liquidity_need: "中等",
  investment_horizon: "12-24个月",
};

const memoryReferences = [
  {
    id: "mem_001",
    type: "偏好",
    summary: "经历过高波动基金后，更偏好回撤较低的产品。",
  },
  {
    id: "mem_002",
    type: "关系",
    summary: "确认配置调整前，通常需要先和配偶达成一致。",
  },
];

const productCandidates = [
  {
    id: "prod_001",
    name: "稳健收益组合 A",
    asset_class: "固收增强",
    risk_level: "R2",
    fit_score: 86,
    reasons: ["匹配低回撤偏好", "适配中等流动性需求"],
  },
  {
    id: "prod_002",
    name: "均衡配置组合 B",
    asset_class: "多资产",
    risk_level: "R3",
    fit_score: 81,
    reasons: ["匹配客户风险等级", "有助于提升组合分散度"],
  },
  {
    id: "prod_003",
    name: "现金管理增强 C",
    asset_class: "现金管理",
    risk_level: "R1",
    fit_score: 73,
    reasons: ["适合作为短期流动性仓位", "可缓冲组合波动"],
  },
];

const brief = {
  title: "模拟客户会前简报",
  summary: "本次沟通重点关注适当性、流动性仓位，以及需与配偶确认的决策流程。",
  talking_points: [
    "先确认客户对风险和此前波动体验的真实感受。",
    "把候选产品放在整体配置角色中解释，不孤立推单。",
    "推进前确认是否需要客户先与配偶沟通一致。",
  ],
};

export const mockTranscript: AGUIEvent[] = [
  {
    type: "RUN_STARTED",
    thread_id: "thread_rm_001",
    run_id: "run_001",
  },
  {
    type: "STEP_STARTED",
    step_name: "skill:pre_meeting_brief",
  },
  {
    type: "CUSTOM",
    name: "rm.skill.output",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      skill: "pre_meeting_brief",
      contract_kind: "rm.pre_meeting_brief",
      contract_version: "0.1.0",
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "surface_customer_001",
      surface: "CustomerProfileCard",
      messages: [
        {
          version: "v0.9",
          createSurface: {
            surfaceId: "surface_customer_001",
            catalogId: "rm-workbench-v0",
          },
        },
        {
          version: "v0.9",
          updateComponents: {
            surfaceId: "surface_customer_001",
            components: [],
          },
        },
        {
          version: "v0.9",
          updateDataModel: {
            surfaceId: "surface_customer_001",
            path: "/",
            data: {
              customer,
              product_candidates: productCandidates,
              memory_references: memoryReferences,
              surface_props: { customer_id: "cust_001", show_memory_highlights: true },
            },
          },
        },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "surface_product_fit_001",
      surface: "ProductFitTable",
      messages: [
        {
          version: "v0.9",
          createSurface: {
            surfaceId: "surface_product_fit_001",
            catalogId: "rm-workbench-v0",
          },
        },
        {
          version: "v0.9",
          updateComponents: {
            surfaceId: "surface_product_fit_001",
            components: [],
          },
        },
        {
          version: "v0.9",
          updateDataModel: {
            surfaceId: "surface_product_fit_001",
            path: "/",
            data: {
              customer,
              product_candidates: productCandidates,
              surface_props: {
                candidate_source: "product_candidates",
                selectable: true,
                min_selection: 1,
                max_selection: 3,
              },
            },
          },
        },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "surface_export_001",
      surface: "BriefExportPanel",
      messages: [
        {
          version: "v0.9",
          createSurface: {
            surfaceId: "surface_export_001",
            catalogId: "rm-workbench-v0",
          },
        },
        {
          version: "v0.9",
          updateComponents: {
            surfaceId: "surface_export_001",
            components: [],
          },
        },
        {
          version: "v0.9",
          updateDataModel: {
            surfaceId: "surface_export_001",
            path: "/",
            data: {
              customer,
              product_candidates: productCandidates,
              brief,
              surface_props: {
                formats: ["Markdown", "PDF 草稿"],
                default_format: "Markdown",
              },
            },
          },
        },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "generic_metric_total_aum",
      surface: "MetricCard",
      messages: [
        { version: "v0.9", createSurface: { surfaceId: "generic_metric_total_aum", catalogId: "rm-workbench-v0" } },
        { version: "v0.9", updateComponents: { surfaceId: "generic_metric_total_aum", components: [{ id: "generic_metric_total_aum_root", component: "MetricCard", props: { label: "管理资产总额", value: "3,200,000", unit: "CNY", trend: "up", delta: "+5.2%" } }] } },
        { version: "v0.9", updateDataModel: { surfaceId: "generic_metric_total_aum", path: "/", data: { block_type: "MetricCard", props: { label: "管理资产总额", value: "3,200,000", unit: "CNY", trend: "up", delta: "+5.2%" } } } },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "generic_allocation_table",
      surface: "DataTable",
      messages: [
        { version: "v0.9", createSurface: { surfaceId: "generic_allocation_table", catalogId: "rm-workbench-v0" } },
        { version: "v0.9", updateComponents: { surfaceId: "generic_allocation_table", components: [{ id: "generic_allocation_table_root", component: "DataTable", props: { columns: [{ key: "asset_class", label: "资产类别" }, { key: "ratio", label: "配置比例" }, { key: "amount", label: "金额 (万)" }], rows: [{ asset_class: "固收增强", ratio: "40%", amount: 128 }, { asset_class: "多资产", ratio: "35%", amount: 112 }, { asset_class: "现金管理", ratio: "25%", amount: 80 }] } }] } },
        { version: "v0.9", updateDataModel: { surfaceId: "generic_allocation_table", path: "/", data: { block_type: "DataTable", props: { columns: [{ key: "asset_class", label: "资产类别" }, { key: "ratio", label: "配置比例" }, { key: "amount", label: "金额 (万)" }], rows: [{ asset_class: "固收增强", ratio: "40%", amount: 128 }, { asset_class: "多资产", ratio: "35%", amount: 112 }, { asset_class: "现金管理", ratio: "25%", amount: 80 }] } } } },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "generic_nav_line",
      surface: "LineChart",
      messages: [
        { version: "v0.9", createSurface: { surfaceId: "generic_nav_line", catalogId: "rm-workbench-v0" } },
        { version: "v0.9", updateComponents: { surfaceId: "generic_nav_line", components: [{ id: "generic_nav_line_root", component: "LineChart", props: { title: "组合净值走势", xKey: "date", series: [{ key: "nav", label: "组合净值", color: "#1570ef" }, { key: "benchmark", label: "基准", color: "#98a2b3" }], data: [{ date: "2025-01", nav: 1.0, benchmark: 1.0 }, { date: "2025-04", nav: 1.03, benchmark: 1.01 }, { date: "2025-07", nav: 1.05, benchmark: 1.02 }, { date: "2025-10", nav: 1.08, benchmark: 1.04 }, { date: "2026-01", nav: 1.12, benchmark: 1.05 }] } }] } },
        { version: "v0.9", updateDataModel: { surfaceId: "generic_nav_line", path: "/", data: { block_type: "LineChart", props: { title: "组合净值走势", xKey: "date", series: [{ key: "nav", label: "组合净值" }, { key: "benchmark", label: "基准" }], data: [{ date: "2025-01", nav: 1.0, benchmark: 1.0 }] } } } },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "generic_revenue_bar",
      surface: "BarChart",
      messages: [
        { version: "v0.9", createSurface: { surfaceId: "generic_revenue_bar", catalogId: "rm-workbench-v0" } },
        { version: "v0.9", updateComponents: { surfaceId: "generic_revenue_bar", components: [{ id: "generic_revenue_bar_root", component: "BarChart", props: { title: "季度收益贡献", xKey: "quarter", series: [{ key: "fixed_income", label: "固收", color: "#067647" }, { key: "multi_asset", label: "多资产", color: "#1570ef" }, { key: "cash", label: "现金", color: "#b54708" }], data: [{ quarter: "Q1", fixed_income: 12000, multi_asset: 8000, cash: 3000 }, { quarter: "Q2", fixed_income: 15000, multi_asset: 10000, cash: 3500 }, { quarter: "Q3", fixed_income: 13000, multi_asset: 11000, cash: 4000 }, { quarter: "Q4", fixed_income: 16000, multi_asset: 12000, cash: 4500 }] } }] } },
        { version: "v0.9", updateDataModel: { surfaceId: "generic_revenue_bar", path: "/", data: { block_type: "BarChart", props: { title: "季度收益贡献", xKey: "quarter", series: [{ key: "fixed_income", label: "固收" }], data: [{ quarter: "Q1", fixed_income: 12000 }] } } } },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "generic_allocation_pie",
      surface: "PieChart",
      messages: [
        { version: "v0.9", createSurface: { surfaceId: "generic_allocation_pie", catalogId: "rm-workbench-v0" } },
        { version: "v0.9", updateComponents: { surfaceId: "generic_allocation_pie", components: [{ id: "generic_allocation_pie_root", component: "PieChart", props: { title: "资产配置分布", labelKey: "category", valueKey: "amount", data: [{ category: "固收增强", amount: 128 }, { category: "多资产", amount: 112 }, { category: "现金管理", amount: 80 }] } }] } },
        { version: "v0.9", updateDataModel: { surfaceId: "generic_allocation_pie", path: "/", data: { block_type: "PieChart", props: { title: "资产配置分布", labelKey: "category", valueKey: "amount", data: [{ category: "固收增强", amount: 128 }, { category: "多资产", amount: 112 }, { category: "现金管理", amount: 80 }] } } } },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "a2ui.surface.messages",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      surface_id: "generic_choice_products",
      surface: "ChoiceList",
      messages: [
        { version: "v0.9", createSurface: { surfaceId: "generic_choice_products", catalogId: "rm-workbench-v0" } },
        { version: "v0.9", updateComponents: { surfaceId: "generic_choice_products", components: [{ id: "generic_choice_products_root", component: "ChoiceList", props: { title: "推荐操作", multiple: false, options: [{ id: "opt_rebalance", label: "执行再平衡", description: "按目标配置比例调整持仓" }, { id: "opt_add", label: "追加配置", description: "增加固收增强仓位" }, { id: "opt_hold", label: "维持现状", description: "当前配置符合预期，暂不调整" }] } }] } },
        { version: "v0.9", updateDataModel: { surfaceId: "generic_choice_products", path: "/", data: { block_type: "ChoiceList", props: { title: "推荐操作", multiple: false, options: [{ id: "opt_rebalance", label: "执行再平衡" }, { id: "opt_add", label: "追加配置" }, { id: "opt_hold", label: "维持现状" }] } } } },
      ],
    },
  },
  {
    type: "CUSTOM",
    name: "rm.pending_interaction.created",
    value: {
      run_id: "run_001",
      thread_id: "thread_rm_001",
      interaction_id: "pi_001",
      surface_id: "surface_product_fit_001",
      action: "select_products",
      blocking: true,
      schema: {
        type: "object",
        properties: {
          selected_product_ids: {
            type: "array",
            items: { type: "string" },
            minItems: 1,
            maxItems: 3,
          },
        },
        required: ["selected_product_ids"],
      },
    },
  },
  {
    type: "STATE_DELTA",
    delta: [
      {
        op: "add",
        path: "/pending_interactions/pi_001",
        value: { status: "waiting", action: "select_products" },
      },
    ],
  },
  {
    type: "STEP_FINISHED",
    step_name: "skill:pre_meeting_brief",
  },
];
