from __future__ import annotations

from django import forms

from .models import Capture, Decision, FaultEvent, Hypothesis, Machine, Observation, Outcome

NOISE_CHOICES = [
    ("wind", "风声"),
    ("speech", "人声覆盖"),
    ("handling", "手持/摩擦噪声"),
    ("competing_machine", "其他设备干扰"),
    ("overload", "麦克风过载"),
    ("unknown", "其他不明干扰"),
]


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ["make", "model", "fleet_id", "serial_number", "hours", "active"]
        labels = {
            "make": "品牌",
            "model": "型号",
            "fleet_id": "场内编号",
            "serial_number": "序列号",
            "hours": "工时",
            "active": "在用",
        }


class FaultEventForm(forms.ModelForm):
    class Meta:
        model = FaultEvent
        fields = [
            "machine",
            "trigger",
            "symptom",
            "location",
            "recent_repair",
            "attachment",
            "environment_notes",
            "work_order_id",
            "workflow_status",
        ]
        labels = {
            "machine": "设备",
            "trigger": "触发原因",
            "symptom": "现场症状",
            "location": "作业位置",
            "recent_repair": "近期维修",
            "attachment": "属具",
            "environment_notes": "环境说明",
            "work_order_id": "工单号",
            "workflow_status": "流程状态",
        }
        widgets = {
            "symptom": forms.Textarea(attrs={"rows": 4}),
            "recent_repair": forms.Textarea(attrs={"rows": 2}),
            "environment_notes": forms.Textarea(attrs={"rows": 2}),
        }


class CaptureForm(forms.ModelForm):
    manual_noise_reasons = forms.MultipleChoiceField(
        label="现场杂音",
        choices=NOISE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Capture
        fields = [
            "stage",
            "raw_file",
            "position_photo",
            "device_label",
            "component",
            "position_text",
            "distance_m",
            "direction",
            "enclosure_state",
            "action",
            "load",
            "displayed_rpm",
            "gain_mode",
            "repeat_index",
            "manual_noise_reasons",
            "related_pre_capture",
        ]
        labels = {
            "stage": "采集阶段",
            "raw_file": "手机原始录音",
            "position_photo": "录音位置照片",
            "device_label": "手机/录音设备",
            "component": "部位或区域",
            "position_text": "录音位置标记",
            "distance_m": "距离（米）",
            "direction": "麦克风方向",
            "enclosure_state": "机罩/门状态",
            "action": "机器动作",
            "load": "负载",
            "displayed_rpm": "显示转速",
            "gain_mode": "增益模式",
            "repeat_index": "重复序号",
            "related_pre_capture": "对应维修前录音",
        }
        help_texts = {
            "raw_file": "支持 WAV、M4A、MP3、AAC、OGG、3GP，单个最大 100 MB。原始文件不可替换。",
            "position_text": "使用可复现的固定标记，例如“主泵壳右侧螺栓上方20厘米”。",
            "related_pre_capture": "维修后录音应选择同一事件中的维修前录音。",
        }

    def __init__(self, *args, event: FaultEvent | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if event is None:
            self.fields["related_pre_capture"].queryset = Capture.objects.none()
        else:
            self.fields["related_pre_capture"].queryset = event.captures.filter(stage=Capture.Stage.PRE)

    def save(self, commit: bool = True):
        instance = super().save(commit=False)
        instance.manual_noise_reasons = list(self.cleaned_data.get("manual_noise_reasons", []))
        if commit:
            instance.save()
        return instance


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ["capture", "statement", "units", "provenance", "quality_status"]
        labels = {
            "capture": "关联录音",
            "statement": "客观观察",
            "units": "单位",
            "provenance": "来源",
            "quality_status": "证据质量",
        }
        widgets = {"statement": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, event: FaultEvent | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["capture"].queryset = event.captures.all() if event else Capture.objects.none()


class HypothesisForm(forms.ModelForm):
    class Meta:
        model = Hypothesis
        fields = [
            "suspected_component",
            "suspected_failure_mode",
            "supporting_evidence",
            "contradicting_evidence",
            "alternatives",
            "confidence",
            "missing_evidence",
            "safest_next_verification",
            "status",
        ]
        labels = {
            "suspected_component": "疑似部位",
            "suspected_failure_mode": "疑似失效模式",
            "supporting_evidence": "支持证据",
            "contradicting_evidence": "反对证据",
            "alternatives": "替代解释",
            "confidence": "置信程度",
            "missing_evidence": "缺失证据",
            "safest_next_verification": "最安全的下一步验证",
            "status": "假设状态",
        }
        widgets = {
            "supporting_evidence": forms.Textarea(attrs={"rows": 3}),
            "contradicting_evidence": forms.Textarea(attrs={"rows": 3}),
            "alternatives": forms.Textarea(attrs={"rows": 2}),
            "missing_evidence": forms.Textarea(attrs={"rows": 2}),
            "safest_next_verification": forms.Textarea(attrs={"rows": 3}),
        }


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = [
            "decision",
            "urgency",
            "risk",
            "authority_basis",
            "reversibility",
            "rollback_action",
            "work_order_id",
            "status",
        ]
        labels = {
            "decision": "人工授权决定",
            "urgency": "紧急程度",
            "risk": "风险依据",
            "authority_basis": "授权依据",
            "reversibility": "可逆性",
            "rollback_action": "回退措施",
            "work_order_id": "工单号",
            "status": "执行状态",
        }
        widgets = {
            "decision": forms.Textarea(attrs={"rows": 3}),
            "risk": forms.Textarea(attrs={"rows": 2}),
            "authority_basis": forms.Textarea(attrs={"rows": 2}),
            "reversibility": forms.Textarea(attrs={"rows": 2}),
            "rollback_action": forms.Textarea(attrs={"rows": 2}),
        }


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = Outcome
        fields = [
            "disposition",
            "confirmed_component",
            "excluded_component",
            "failure_mode",
            "inspection_evidence",
            "parts",
            "adjustments",
            "before_after_comparison",
            "residual_uncertainty",
            "closure_status",
            "post_captures",
        ]
        labels = {
            "disposition": "结果类型",
            "confirmed_component": "确认部位",
            "excluded_component": "排除部位",
            "failure_mode": "确认失效模式",
            "inspection_evidence": "检查/维修证据",
            "parts": "更换零件",
            "adjustments": "调整内容",
            "before_after_comparison": "维修前后对比",
            "residual_uncertainty": "剩余不确定性",
            "closure_status": "关闭状态",
            "post_captures": "维修后录音",
        }
        widgets = {
            "inspection_evidence": forms.Textarea(attrs={"rows": 4}),
            "parts": forms.Textarea(attrs={"rows": 2}),
            "adjustments": forms.Textarea(attrs={"rows": 2}),
            "before_after_comparison": forms.Textarea(attrs={"rows": 3}),
            "residual_uncertainty": forms.Textarea(attrs={"rows": 2}),
            "post_captures": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, event: FaultEvent | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["post_captures"].queryset = (
            event.captures.filter(stage=Capture.Stage.POST) if event else Capture.objects.none()
        )


class UnresolvedDispositionForm(forms.ModelForm):
    class Meta:
        model = FaultEvent
        fields = [
            "unresolved_reason",
            "unresolved_next_condition",
            "unresolved_owner",
            "unresolved_due_date",
        ]
        labels = {
            "unresolved_reason": "当前无法闭环的原因",
            "unresolved_next_condition": "下次复核条件",
            "unresolved_owner": "负责人",
            "unresolved_due_date": "计划复核日期",
        }
        widgets = {
            "unresolved_reason": forms.Textarea(attrs={"rows": 3}),
            "unresolved_next_condition": forms.Textarea(attrs={"rows": 3}),
            "unresolved_due_date": forms.DateInput(attrs={"type": "date"}),
        }
