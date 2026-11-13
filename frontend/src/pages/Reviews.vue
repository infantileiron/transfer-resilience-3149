<script setup lang="ts">
import {ref,computed} from 'vue';
import type {Workspace} from '../stores/workspace';
import PageHeading from '../components/common/PageHeading.vue';
import Notice from '../components/common/Notice.vue';
import Empty from '../components/common/Empty.vue';
import PhaseCompare from '../components/PhaseCompare.vue';
import {create as review} from '../api/reviews';
import {create as report} from '../api/reports';
import * as reportsApi from '../api/reports';
import {download} from '../api/client';
import {useAsync} from '../hooks/useAsync';
import {DECISIONS} from '../constants/enums';
import {date} from '../utils/format';
const props=defineProps<{data:Workspace;canWrite:boolean;isAdmin:boolean;refresh:()=>Promise<void>}>();
const completed=computed(()=>props.data.runs.filter(r=>r.status==='completed'));
const id=ref(''),note=ref(''),decision=ref('accepted');
const active=computed(()=>completed.value.find(r=>r.id===id.value)||completed.value[0]);
const {busy,error,execute}=useAsync();
const notice=ref('');
const opened=ref('');
const versions=ref<Record<string,import('../types/domain').Report[]>>({});
const openedRun=computed(()=>completed.value.find(r=>r.id===opened.value));
const latest=computed(()=>props.data.reviews.find(r=>r.run_id===active.value?.id));
const latestAccepted=computed(()=>latest.value?.decision==='accepted');
const archivedFor=computed(()=>props.data.reports.find(p=>p.run_id===active.value?.id&&p.status==='valid'));
async function loadVersions(runId?:string){if(!runId)return;const data=await reportsApi.versions(runId);versions.value={...versions.value,[runId]:data.versions};opened.value=runId}
async function submit(){await execute(async()=>{await review({run_id:active.value?.id,note:note.value,decision:decision.value});note.value='';await props.refresh()})}
async function publish(){if(!active.value||!latest.value)return;await execute(async()=>{const created=await report({run_id:active.value!.id,review_id:latest.value!.id,title:'中转网络韧性人工复核 · '+new Date().toISOString().slice(0,10)});notice.value=`绑定复核意见归档为第 ${created.version} 版（${created.status==='valid'?'有效':'已失效'}）。`;await loadVersions(active.value!.id);await props.refresh()})}
async function fetchVersion(p:import('../types/domain').Report){await execute(async()=>{const result=await download(p.id,p.version);notice.value=result.invalid?`已下载第 ${p.version} 版，该版本已失效：${result.reason}`:`已下载第 ${p.version} 版（有效）。`})}
function versionsFor(runId:string){return versions.value[runId]}
function statusText(p:import('../types/domain').Report){return p.status==='valid'?'有效':'已失效'}
</script>
<template>
<PageHeading code="06 / RESILIENCE REVIEW" title="把瓶颈与绕行，放回各自口径。" description="记录边容量、割集、守恒和最短路证据，不能把最大流说成沿最短路发运。归档绑定当次接受意见，后续复核可使其失效。"/>
<PhaseCompare v-if="active" :result="active.result"/>
<section class="paper" v-if="canWrite">
 <h2>提交韧性复核</h2>
 <form class="grid-form" @submit.prevent="submit">
  <label>已完成推演<select aria-label="复核推演记录" :value="active?.id" @change="id=($event.target as HTMLSelectElement).value"><option v-for="r in completed" :key="r.id" :value="r.id">{{data.scenarios.find(s=>s.id===r.scenario_id)?.name}} · {{r.created_at.slice(11,19)}}</option></select></label>
  <label>复核判断<select v-model="decision"><option value="accepted">接受并记录边界</option><option value="needs_attention">需要继续核查</option></select></label>
  <label class="wide">依据与边界<textarea aria-label="依据与边界" required minlength="8" rows="3" v-model="note" placeholder="记录逐边ID、maxflow=mincut、节点守恒、停用影响与独立最短路，不作实际发运指令。"/></label>
  <button :disabled="busy||!active">提交韧性复核</button>
 </form>
</section>
<Notice v-if="error" error>{{error}}</Notice>
<Notice v-if="notice">{{notice}}</Notice>
<section class="paper">
 <h2>人工复核记录</h2>
 <Empty v-if="!data.reviews.length">运行完成后，先核对容量/守恒/路径三类证据，再提交判断。</Empty>
 <article class="review-record" v-for="r in data.reviews" :key="r.id">
  <div><span :class="['status',r.decision]">{{DECISIONS[r.decision]}}</span><small>{{r.author}} · {{date(r.created_at)}}</small></div>
  <p>{{r.note}}</p>
  <small v-if="r.decision==='needs_attention'&&data.reports.some(p=>p.run_id===r.run_id&&p.invalidated_review_id===r.id)" class="invalidation-hint">该意见已使本次推演的既有归档失效。</small>
 </article>
</section>
<section class="paper">
 <div class="section-heading"><h2>网络图册归档</h2><span v-if="latest">当次接受意见：{{latestAccepted?'已接受':'需继续核查'}} · {{latest.author}} · {{date(latest.created_at)}}</span></div>
 <div class="archive-actions" v-if="isAdmin">
  <button :disabled="busy||!latestAccepted||!!archivedFor" @click="publish">{{archivedFor?'当次接受意见已归档':'批准并归档当次接受意见'}}</button>
  <small v-if="!latestAccepted">最新复核意见不是接受，归档不可用；需重新核查后再接受。</small>
  <small v-else-if="archivedFor">同次接受意见重复归档返回第 {{archivedFor.version}} 版，不新增版本。</small>
 </div>
 <Empty v-if="!data.reports.length">接受复核后由管理员归档；归档绑定当次接受意见与推演结果。</Empty>
 <article class="report-row" v-for="p in data.reports" :key="p.id">
  <div>
   <h3>第 {{p.version}} 版 · {{p.title}} <span :class="['status',p.status]">{{statusText(p)}}</span></h3>
   <small>{{date(p.created_at)}} · {{p.published_by}} · 绑定复核 {{p.review_id?.slice(0,8)||'未绑定'}} · {{p.accepted_author}}</small>
   <small>接受意见：{{p.accepted_note}}</small>
   <small v-if="p.summary">结果摘要：基线最大流 {{p.summary.baseline_maxflow}} → 停用 {{p.summary.outage_maxflow}}；割容量 {{p.summary.cut_capacity}}；停用最短时长 {{p.summary.outage_reachable?p.summary.outage_shortest_minutes+' 分钟':'不可达'}}</small>
   <small v-if="p.status!=='valid'" class="invalid-reason">失效 {{date(p.invalidated_at)}} · {{p.invalidated_by}}：{{p.invalidated_reason}}</small>
  </div>
  <div class="report-buttons">
   <button class="secondary" :disabled="busy" @click="fetchVersion(p)">下载第 {{p.version}} 版CSV　↓</button>
   <button class="secondary" :disabled="busy" @click="execute(()=>loadVersions(p.run_id))">查看该推演各版</button>
  </div>
 </article>
 <div v-if="opened&&versionsFor(opened)" class="version-list">
  <h3>该推演归档版本 · {{data.scenarios.find(s=>s.id===openedRun?.scenario_id)?.name}} · {{openedRun?.created_at.slice(11,19)}}</h3>
  <div class="table-scroll"><table><thead><tr><th>版本</th><th>状态</th><th>绑定复核</th><th>接受意见</th><th>操作</th></tr></thead><tbody>
   <tr v-for="v in versionsFor(opened)" :key="v.id" :class="{invalid:v.status!=='valid'}">
    <td>第 {{v.version}} 版</td>
    <td><span :class="['status',v.status]">{{statusText(v)}}</span></td>
    <td><b>{{v.review_id?.slice(0,8)||'未绑定'}}</b><small>{{v.accepted_author}} · {{date(v.created_at)}}</small></td>
    <td>{{v.status==='valid'?v.accepted_note:v.invalidated_reason}}<small v-if="v.summary">基线最大流 {{v.summary.baseline_maxflow}} → 停用 {{v.summary.outage_maxflow}}；割容量 {{v.summary.cut_capacity}}；停用最短时长 {{v.summary.outage_reachable?v.summary.outage_shortest_minutes+' 分钟':'不可达'}}</small></td>
    <td><button class="secondary" :disabled="busy" @click="fetchVersion(v)">下载CSV　↓</button></td>
   </tr></tbody></table></div>
 </div>
</section>
<details class="audit-details"><summary>操作留痕 / 最近{{data.audit.length}}条</summary><div class="table-scroll"><table><thead><tr><th>操作者</th><th>动作</th><th>状态</th></tr></thead><tbody><tr v-for="a in data.audit" :key="a.id"><td>{{a.actor}}</td><td>{{a.action}}</td><td>{{a.status}}</td></tr></tbody></table></div></details>
</template>
