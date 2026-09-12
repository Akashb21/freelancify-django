from django import forms
from .models import Job, Proposal

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'category', 'description', 'budget_type', 'budget_min', 'budget_max', 'experience_level', 'skills_required')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white focus:outline-none focus:border-cyan-500 placeholder-slate-500'
            })


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ('bid_amount', 'estimated_days', 'cover_letter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 bg-slate-900/80 border border-slate-700/60 rounded-xl text-white focus:outline-none focus:border-cyan-500 placeholder-slate-500'
            })
