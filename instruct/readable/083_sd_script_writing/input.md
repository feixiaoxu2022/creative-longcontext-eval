# 系统设定

# 短剧创作助手 — 创作规则

你是一名专业的短剧创作助手，能够创作8种题材的短剧，从选题到剧本完成完整流程。

## 创作阶段说明

创作流程分为以下阶段，本次任务将指定你完成其中某一阶段：

### 阶段1：选题简报

**目标**：确认题材和集数，输出选题简报（JSON格式）。

### 阶段2：角色设计

**目标**：设计完整的角色体系（JSON格式）。

**要求**：
- 主角≥2个，配角+反派≥2个，总计≥4个命名角色
- 每个角色需要完整的9维度设计（详见参考文档中的skill手册）
- 不同题材对反派数量有不同要求（详见题材手册）

### 阶段3：情节总纲

**目标**：设计整体故事弧线和分集大纲（JSON格式）。

**要求**：
- 先构思整体故事弧线（起承转合），再展开到每一集
- 每集大纲包含：hook（钩子）、conflict（冲突）、twist（反转）、emotional_peak（情绪峰值）、scenes（场景列表）、characters_involved（角色名单）
- 务必在大纲阶段充分规划情节，确保情节密度足够，避免后期写剧本时疲软注水
- 大纲中的角色名称必须与角色设定中的 `character_name` 完全一致

### 阶段4：分集剧本创作

**目标**：按大纲逐集创作剧本（JSON格式）。

**要求**：
- 按集号顺序创作
- 剧本必须忠实于大纲设定的hook、conflict、twist、emotional_peak

---

## 支持的题材

| 题材ID | 中文名 |
|--------|--------|
| `sweet_romance` | 都市甜宠 |
| `revenge_drama` | 复仇爽剧 |
| `family_saga` | 年代家庭 |
| `mystery_thriller` | 悬疑推理 |
| `ancient_court` | 古装权谋 |
| `transmigration` | 穿越重生 |
| `underdog_comeback` | 战神逆袭 |
| `son_in_law` | 赘婿 |

如果用户要求的题材不在上述列表中，拒绝创作并说明原因。

---

## 关键约束

### 集数
- **必须完成用户指定的所有集数**

### 角色
- **命名角色**（有具体姓名）：必须在角色设定中定义
- **群众角色**（"宾客们""路人"等）：可直接在剧本中使用，无需定义

### 跨阶段一致性
- 大纲 `characters_involved` 中的角色名 = 角色设定中的 `character_name`
- 剧本中有姓名的角色必须在角色设定中存在
- 每集剧本 `total_scenes` = 对应大纲集 `scenes` 数组长度

### 用户约束融入
- 用户指定的角色设定、主题、冲突、结局、开场等约束必须在创作中体现
- 用户提供的故事前提/梗概，必须以此为基础展开，不能另起炉灶

### 内容质量底线
- **题材一致**：输出内容必须匹配用户指定的题材
- **角色一致**：角色表现必须符合角色设定
- **逻辑自洽**：不能有前后矛盾的情节
- **情节密度**：每集剧本必须有实质内容推进，不可注水



# 用户需求

做一部30集年代家庭短剧。要有史诗感但不要假大空——不是写一个家庭和国家命运绑定的那种，而是普通人家在时代洪流中被裹挟、挣扎、妥协、坚持的故事。主线是一个家庭的分分合合，但每个家庭成员都要有自己独立的人物弧光，不能只是"为了大家庭牺牲小自我"的工具人。



# 参考文档


## ancient_court_skill.md





## family_saga_skill.md





## mystery_thriller_skill.md





## revenge_drama_skill.md





## shortdrama_general_skill.md





## son_in_law_skill.md





## sweet_romance_skill.md

# 都市甜宠短剧创作手册

> 本手册为都市甜宠题材的专属创作指南。通用创作方法论请参阅《短剧通用创作技能手册》。

---

## 一、题材核心特征

**情绪基调**：轻松愉悦、小虐怡情
**目标受众**：18-34岁女性
**核心价值主张**：高强度情绪推进 + 密集反转 + 强CP化学反应

### 题材特色

都市甜宠以现代都市为背景，讲述男女主角从相遇到相爱的浪漫故事。核心在于"甜"与"宠"的平衡：

- **甜**：高频率的甜蜜互动、撒糖场景、温暖细节
- **宠**：男主对女主的呵护、溺爱、无底线包容
- **小虐**：适度的误会、小波折增加情绪起伏，但不能过度虐心

---

## 二、钩子核心元素

### 1. 身份反差
打破常规认知的身份对比。

- 示例："总裁大人白天高冷禁欲，晚上竟然跪求女主原谅"（25字）
- 示例："身价百亿的他，为了追我甘愿做我的贴身助理"（22字）

### 2. 危机
立即引发关注的冲突或困境。

- 示例："合同婚姻第一天，他就说要和我离婚"（18字）
- 示例："被渣男抛弃当天，霸道总裁说要娶我"（17字）

### 3. 目标
明确的欲望或追求。

- 示例："三十天内，我要让这个冰山总裁爱上我"（18字）
- 示例："为了报复前男友，我决定追求他的死对头"（19字）

---

## 三、典型角色原型库

> 以下仅为参考示例。请根据剧情需要自行创作角色。

### 主角原型：冰山霸总

- **identity**: 跨国集团总裁
- **gap**: 情感表达障碍，童年缺爱导致不懂如何爱人
- **desire**: 事业成功，掌控一切
- **secret**: 十年前曾暗恋女主，因误会错过
- **motivation**: 保护家族企业，证明自己的价值
- **contrast**: 外表高冷禁欲，内心宠溺专一
- **catchphrase**: "你敢！"
- **role_type**: protagonist

### 主角原型：独立女主

- **identity**: 广告公司创意总监
- **gap**: 不信任男性，情感防御过强
- **desire**: 事业独立，不依附任何人
- **secret**: 曾被前男友背叛，差点失去一切
- **motivation**: 证明女性价值，活出自我
- **contrast**: 职场女强人，恋爱时却会脸红心跳
- **catchphrase**: "我可以"
- **role_type**: protagonist

### 配角原型：毒舌闺蜜

- **identity**: 时尚杂志编辑
- **gap**: 恐婚，害怕重复父母的悲剧
- **desire**: 活出精彩人生，不被婚姻束缚
- **secret**: 暗中帮助女主解决危机
- **motivation**: 守护闺蜜的幸福
- **contrast**: 嘴上毒舌，行动上暖心
- **catchphrase**: "你这是恋爱脑"
- **role_type**: supporting

### 反派原型：白莲花前女友

- **identity**: 名媛，男主前女友
- **gap**: 极度自恋，无法接受失去
- **desire**: 重新得到男主
- **secret**: 当年主动分手是为了攀高枝
- **motivation**: 不甘心失去优质资源
- **contrast**: 表面温柔大方，实则心机深重
- **catchphrase**: "琛哥，我们之间那么多回忆..."
- **role_type**: antagonist

---

## 四、甜宠节奏设计

### 糖密度标准

- **每集至少2个甜蜜高光时刻**
- **情绪曲线**：小虐→高甜→小虐→高甜（波浪式推进）
- **反转频率**：每集至少1个身份/信息差反转

### 常见甜点类型

1. **身份反转甜**：大佬真实身份曝光，女主震惊
2. **霸道宠溺甜**：男主护短、吃醋、秀恩爱
3. **肢体互动甜**：壁咚、摸头杀、公主抱
4. **语言撩拨甜**：情话攻势、暧昧对话
5. **细节关怀甜**：记住小习惯、默默守护

### 小虐控制原则

- **虐点目的**：增加情绪落差，放大后续甜度
- **时长控制**：单次虐点不超过1集，避免观众流失
- **虐的方向**：误会、身份差距、外力阻挠，但绝不能是男主主动伤害女主
- **解虐速度**：快速解释清楚，不拖泥带水

---

## 五、成功案例参考

### 案例1：《夜总裁的替身甜妻》

**成功要素**：
- **钩子**："合同夫妻第一夜，他把我当成了白月光"（身份反差+危机）
- **角色反差**：男主表面冷漠，实则深情；女主表面柔弱，实则坚韧
- **糖密度**：每集2-3个高甜场景
- **小虐控制**：误会在1集内解开，不拖沓

### 案例2：《闪婚总裁太难缠》

**成功要素**：
- **钩子**："闪婚当天才发现，老公是我顶头上司"（身份反差）
- **节奏把控**：前3集完成从陌生到心动的情感进阶
- **冲突设计**：职场身份差+婚姻关系，双重张力
- **情感峰值**：第3集男主为女主在董事会上力排众议

---

**注意**：都市甜宠的核心魅力在于"甜到上头"，避免过度加虐或过多商战支线。观众来看的是恋爱，不是职场剧。商战/家族矛盾只是推动感情线的工具，不是主线。



## transmigration_skill.md





## underdog_comeback_skill.md





# 已有创作成果


## 角色卡


### characters.json

{
 "characters": [
 {
 "character_name": "刘凤兰",
 "identity": "李家母亲，纺织厂下岗女工，家庭主妇",
 "gap": "将所有希望寄托在孩子身上，忽略自我：年轻时曾是文艺青年，梦想成为老师",
 "desire": "让每个孩子都过上好日子，家庭和睦团圆",
 "secret": "孩子出生时大出血留下了隐患，常年隐瞒家人，独自承受病痛",
 "motivation": "延续丈夫李建国的期望，弥补当年未能支持他的遗憾",
 "contrast": "对外坚强如铁，独处时偷偷流泪；表面乐观坚强，内心却极度脆弱",
 "catchphrase": "一家人在一起比什么都重要，什么苦都值得",
 "role_type": "protagonist",
 "backstory": "50年代出生，经历过困难时期，后来嫁给纺织厂技术员李建国。下岗后全力支持丈夫创业，管好家内一切事务。",
 "relationships": ["李建国（丈夫）", "李秀芳（长女）", "李明（儿子）"]
 },
 {
 "character_name": "李建国",
 "identity": "李家父亲，从国企下岗后创业的个体户",
 "gap": "大男子主义，不善表达感情：总觉得男人应该撑起天，却不知道家人需要什么",
 "desire": "让家人过上好日子，证明当年坚持是对的",
 "secret": "当年为了家庭稳定选择了安稳工作，放弃了初恋搭上的上升机会，内心一直有遗憾",
 "motivation": "用肩膀扛起整个家，弥补年轻时未能给家人更好生活的歉疚",
 "contrast": "在家严厉沉默，在外为家拼命；表面冷漠固执，内心却极其柔软",
 "catchphrase": "男人哭什么哭，这个家需要你顶起来",
 "role_type": "protagonist",
 "backstory": "60年代出生，国企技术员，下岗后开小卖部创业。经历过改革开放浪潮，性格坚韧但有时过于固执。",
 "relationships": ["刘凤兰（妻子）", "李秀芳（长女）", "李明（儿子）"]
 },
 {
 "character_name": "李秀芳",
 "identity": "李家长女，省城大学毕业生，回乡创业者",
 "gap": "渴望自由但对家庭有负罪感：追求事业与传统家庭责任之间的冲突",
 "desire": "证明一个女人可以在家乡创造价值，不用都说女人该嫁人",
 "secret": "高考时故意没考好，是为了不让弟弟没有人学威胁弟弟辍学",
 "motivation": "证明新一代的选择是对的，既爱家又爱外面的世界",
 "contrast": "嘴上说要远走高飞，心里放不下家；看似强势独立，实则对家庭有深深愧疚",
 "catchphrase": "这个家太小了，装不下我的梦，但这里永远是我的根",
 "role_type": "supporting",
 "backstory": "70年代出生，高三那年考上一流大学，但因为弟弟要辍学而放低目标。后来在省城打拼多年，回乡创业。",
 "relationships": ["刘凤兰（母亲）", "李建国（父亲）", "李明（弟弟）"]
 },
 {
 "character_name": "赵桂芳",
 "identity": "邻居，社区居委会主任，退休教师",
 "gap": "利益至上，缺乏同理心：过于看重利益，对邻里间的互助精神已经淡薄",
 "desire": "从李家获取经济利益，攀比李家的成功",
 "secret": "当年因嫉妒刘凤兰嫁给李建国，一直放不下这段往事",
 "motivation": "嫉妒和贪婪，认为李家的一切都该分一部分给自己",
 "contrast": "关系好时亲如一家，利益冲突时翻脸不认人；表面热心助人，内心阴暗算计",
 "catchphrase": "这年头，谁还讲那些旧情分，各人过各人的好",
 "role_type": "antagonist",
 "backstory": "与刘凤兰同龄，同样来自纺织厂。退休后进入居委会任职，是社区里有影响力的人物。"
 },
 {
 "character_name": "李明",
 "identity": "李家次子，大学毕业后在省城工作",
 "gap": "渴望自由但对家庭有负罪感：思想进步但被传统观念束缚",
 "desire": "在大城市站稳脚跟，证明当年姐姐牺牲是值得的",
 "secret": "知道姐姐当年故意考低分是因为自己要辍学，一直心里愧疚",
 "motivation": "弥补小时候对姐姐造成的负担，证明自己不会让家失望",
 "contrast": "嘴上说要大城市，心里牵挂家里的改变，既渴望现代生活又放不下家庭",
 "catchphrase": "大城市挺好，但你家永远在心口上",
 "role_type": "supporting",
 "backstory": " yılında doğdu，比姐姐小几岁。姐姐高消费他上大学，后来考上了大学，在省城工作。"
 }
 ]
}



## 分集大纲


### outline.json

{
 "total_episodes":30,
 "story_synopsis": "20世纪80-90年代，一个普通工人家庭在改革开放浪潮中经历的分分合合。父母从国企下岗，卷入时代变迁；儿女在传统观念与新思维之间艰难抉择。每个成员都在挣扎中做出选择，有人妥协，有人坚持，有人在时代洪流中找到了自己的位置。",
 "arc_description": "第一幕（1-10集）：家庭危机与重启。父亲下岗，母亲下岗通知，家庭面临经济危机.Quadfamily fortress to support each other. The family decides to face the challenges together and start anew. 第二幕（11-20集）：时代变革与家庭分裂。兄弟姐妹面临不同选择：姐姐回乡创业，弟弟去大城市。 Parents worry about separation and maintain communication. 第三幕（21-30集）：代价与和解、收获。 Past secrets revealed, familial conflicts resolved, each member finds their position, family reunites in a new form.",
 "episodes": [
 {
 "episode_number":1,
 "hook": "下岗通知书送到家的那天，母亲在门外偷偷擦干眼泪，父亲却拍着胸口说'没事，我能解决'。",
 "conflict": "父亲下岗，家庭面临经济危机，但父亲不愿承认，执意要找新工作",
 "twist": "父亲偷偷卖掉祖屋，筹集资金准备创业，这个决定未与家人商量",
 "emotional_peak": "夜深人静时，母亲独自落泪的照片被丈夫发现",
 "scenes": ["工厂门口接到下岗通知", "家中晚饭时的沉默", "父亲深夜变卖祖产"],
 "characters_involved": ["刘凤兰", "李建国"],
 "title": "通知到达"
 },
 {
 "episode_number":2,
 "hook": "母亲在夜市摆摊的第一天，顾客嘲笑她是'下岗女工'，她却笑着擦掉菜上的尘土继续卖。",
 "conflict": "母亲下岗后决定夜市摆摊，遭到父亲反对，认为丢人",
 "twist": "母亲用第一个月赚的钱给丈夫买了一件衬衣，代替了下岗期间的委屈",
 "emotional_peak": "父亲看着妻子粗糙的双手，第一次说'辛苦了'",
 "scenes": ["夜市摆摊", "家庭争论", "父亲发现母亲手上的伤口"],
 "characters_involved": ["刘凤兰", "李建国"],
 "title": "第一桶金"
 },
 {
 "episode_number":3,
 "hook": "长女秀芳成年礼上，她倾囊变卖自己写满笔记的课本，只为换钱给母亲买药。",
 "conflict": "母亲 illness 加重，秀芳想辍学照顾，被父亲强制性让继续学业",
 "twist": "父亲发现秀芳课本上的如同 Maple 涂鸦，知道她有多压抑",
 "emotional_peak": "秀芳риlager the day before school, family discussion led to compromise on tuition fees",
 "scenes": ["成人礼羞辱", "医院夜晚", "家庭争执解决"],
 "characters_involved": ["刘凤兰", "李建国", "李秀芳"],
 "title": "重大选择"
 },
 {
 "episode_number":4,
 "hook": "改开的春风，父亲把家里最后的积蓄要去个体户，母亲却在担心'money is hard-earned'，担心他赔光。",
 "conflict": "父亲决定开小卖部创业，母亲担心他冒险失败",
 "twist": "他发现初恋在深圳过得很好，这让他对创业更加坚定",
 "emotional_peak": "开业第一天生意冷清，母亲默默帮忙一起叫卖",
 "scenes": ["家庭讨论创业", "小卖部开业", "深夜家庭算账"],
 "characters_involved": ["刘凤兰", "李建国"],
 "cliffhanger": "第二天，工商部门突击检查，小卖部面临被查封的风险"
 }
 ]
}



## 已完成剧本


### scripts/episode_10_script.json

{
 "episode_number":10,
 "total_scenes":3,
 "title":"第一幕결び",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"小卖部",
 "time":"白天",
 "atmosphere":"漸漸営業izzy"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "顾客们"],
 "content": [
 {
 "type":"action",
 "description":"小卖部比以来更忙碌，李建国能够熟练地应对各种顾客"
 },
 {
 "type":"dialogue",
 "character":"顾客甲",
 "text":"老李，你这店是越开越好了，再这样下去要成咱们这片的大店老板了。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"哈哈，张叔叔过奖了，就是小本生意，糊口还成，大的钱可挣不了。"
 },
 {
 "type":"action",
 "description":"李建国忙着收钱找零，脸上洋溢着满足的笑容"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，今天算了账，这个月比 painstakingfulWidget.cpp 時期賺了多啊。"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨的家庭氛围"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰", "李秀芳"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸妈，今天是我生日，我们出去吃饭庆祝一下吧。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"生日？（意外地）你不说我都忘记了。羽菲，生日快乐！"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"是啊，咱们秀芳也16了，小时候那个爱哭的小丫头，现在都要成大人了。"
 },
 {
 "type":"action",
 "description":"一家人围坐在一起，庆祝这个特殊的日子"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸，妈，谢谢你们的努力，这个家才能不停地 episode by episode towards the future。"
 }
 ]
 },
 {
 "scene_header": {
 "location":"街道",
 "time":"夜晚",
 "atmosphere":"Starry idea"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"才发现我們這樣挣扎過來，滿懷希望的家庭，多麼不容易。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"是啊，凤兰，像我們這樣的普通家庭，能有今天真的不容易。"
 },
 {
 "type":"emotion",
 "description":"两人一起望着星空，心中充满了希望和对未来的期待"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"不过，只是好？这只是开始罢了。未来的生活，会更美好。"
 },
 {
 "type":"emotion",
 "description":"月光下，两人的背影显得格外坚定，向着命运倾诉成的，在未來將會有多少變化向著平民的街道 detailed。"
 }
 ]
 }
 ]
}



### scripts/episode_11_script.json

{
 "episode_number":11,
 "total_scenes":3,
 "title":"扩展的想法",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"小卖部",
 "time":"白天",
 "atmosphere":"忙碌的小卖部"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "顾客们"],
 "content": [
 {
 "type":"action",
 "description":"小卖部生意兴隆，顾客络绎不绝"
 },
 {
 "type":"dialogue",
 "character":"顾客甲",
 "text":"老李，你这东西再多些就更好了，我看有些超市都没有你这全。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"您老说得太对了，我最近也在想怎么把范围扩大，进更多样的商品来。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，你这是要扩大规模了？那就不只是小卖部了啊。"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨的家庭讨论"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，我想把店铺做大些，卖更多的商品。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，你的意思是？像超市那样？"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"是啊，我们愿意冒更大的险，做真正意义上的超市。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"能行吗？我们现在钱不多..."（有些犹豫）
 },
 {
 "type":"action",
 "description":"李建国握住妻子的手，眼中充满信心"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，你早就陪了我三年了，没有你我也做不到今天。这次你也要加油，我一定会成功的！"
 }
 ]
 },
 {
 "scene_header": {
 "location":"街道",
 "time":"傍晚",
 "atmosphere":"车来车往的街道"
 },
 "scene_number":3,
 "characters":["李秀芳", "同学"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"这次他们真要扩张了，我有些担心。"
 },
 {
 "type":"dialogue",
 "character":"同学",
 "text":"秀芳，你父母真的很有魄力，这样的魄力让我们很羡慕。"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"希望能顺利吧。我会努力学好本事，将来也能帮家里的忙。"
 },
 {
 "type":"emotion",
 "description":"李秀芳看着街道，心中对家庭未来充满担忧但又有希望"
 }
 ]
 }
 ]
}



### scripts/episode_12_script.json

{
 "episode_number":12,
 "total_scenes":3,
 "title":"扩张的日子",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"小卖部",
 "time":"白天",
 "atmosphere":"繁忙的扩张期"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "工人"],
 "content": [
 {
 "type":"action",
 "description":"小卖部正在进行扩张，工人正在搬运新货架"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，你看这些货架，比以前的气派多了！"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，你真的太厉害了，这么多东西我一个人肯定忙不过来。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"没事，慢慢学，这些天我会一直陪在你身边的。"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"忙碌的准备"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，明天开业，万一没人来怎么办？"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"放心，我已经发了不少传单，肯定会来的！"
 },
 {
 "type":"action",
 "description":"李建国信心勃勃地收拾最后的货物"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"这是我们人生最重要的一次转折，一定要成功！"
 }
 ]
 },
 {
 "scene_header": {
 "location":"街道",
 "time":"黄昏",
 "atmosphere":"夕阳下的街道"
 },
 "scene_number":3,
 "characters":["李秀芳", "李明"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"弟弟，明天就是爸妈超市开业的大日子了，你一定要来看啊！"
 },
 {
 "type":"dialogue",
 "character":"李明",
 "text":"姐，我就在省城，肯定赶回去！"
 },
 {
 "type":"emotion",
 "description":"姐弟俩在夕阳下相拥，家人的团聚让他们的心都温暖了"
 }
 ]
 }
 ]
}



### scripts/episode_13_script.json

{
 "episode_number":13,
 "total_scenes":3,
 "title":"盛大的开业",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"超市门口",
 "time":"早晨",
 "atmosphere":"熙熙攘攘的人群，丰收的期待"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "顾客们"],
 "content": [
 {
 "type":"action",
 "description":"超市门口人山人海，鞭炮声此起彼伏"
 },
 {
 "type":"dialogue",
 "character":"顾客甲",
 "text":"李老板，恭喜恭喜啊！新超市气派！"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"谢谢张叔叔！您老先请，今天所有商品都给您打折！"
 },
 {
 "type":"action",
 "description":"李建国忙得不可开交，但脸上挂着幸福的笑容"
 }
 ]
 },
 {
 "scene_header": {
 "location":"超市内",
 "time":"上午",
 "atmosphere":"繁忙的购物现场"
 },
 "scene_number":2,
 "characters":["刘凤兰", "顾客们"],
 "content": [
 {
 "type":"dialogue",
 "character":"顾客乙",
 "text":"刘老板娘，你这超市的商品真全，比别处还便宜！"
 },
 {
 "type":"action",
 "description":"刘凤兰熟练地称重、找零"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"那就谢谢惠顾了，以后常来！今天开业大酬宾！"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨庆祝"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰", "李秀芳", "李明"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸妈，今天生意那么好，你们开心吗？"
 },
 {
 "type":"dialogue","character":"李建国","text":"开心！太开心了！"},
 {"type":"dialogue","character":"刘凤兰","text":"只要你们好好的，我就开心。"},{"type":"emotion","description":"全家庆祝，这是他们努力的结果"}]
 }
 ]
}



### scripts/episode_14_script.json

{
 "episode_number":14,
 "title":"生意兴隆",
 "total_scenes":3,
 "scenes_detail": [
 {
 "scene_header": {"location":"超市", "time":"白天", "atmosphere":"繁忙"},
 "scene_number":1,
 "characters": ["李建国", "顾客"],
 "content": [
 {"type":"action","description":"超市生意火爆，李建国忙得团团转"},{"type":"dialogue","character":"顾客","text":"老李，你这超市真是越开越好！"},{"type":"dialogue","character":"李建国","text":"谢谢！您满意就好！"}]
 },
 {
 "scene_header":{"location":"街道", "time":"傍晚", "atmosphere":"平静"},
 "scene_number":2,
 "characters":["刘凤兰"],
 "content": [
 {"type":"action","description":"刘凤兰打扫完卫生，一个人坐在店里算账"},{"type":"dialogue","character":"刘凤兰","text":"（自言自语）照这样下去，一个月能赚不少钱呢。"},{"type":"emotion","description":"看到账本上的数字，她露出幸福的微笑"}]
 },
 {
 "scene_header":{"location":"李家", "time":"晚上","atmosphere":"温馨"},
 "scene_number":3,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {"type":"dialogue","character":"李建国","text":"凤兰，你太辛苦了，我还是心疼你。"},{"type":"dialogue","character":"刘凤兰","text":"建国，我为你做这些都不觉得苦。"},{"type":"emotion","description":"夫妻俩相视而笑，感情更加深厚"}]
 }
 ]
}



### scripts/episode_15_script.json

{
 "episode_number":15,
 "title":"新的挑战",
 "total_scenes":3,
 "scenes_detail": [
 {
 "scene_header":{"location":"超市", "time":"白天", "atmosphere":"繁忙"},
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "邻居"],
 "content": [{"type":"dialogue","character":"邻居","text":"老李，生意真好啊，比我当初预测的好多了。"},{"type":"dialogue","character":"李建国","text":"都托大家的福。"},{"type":"action","description":"李建国忙得不可开交"}]
 },
 {
 "scene_header":{"location":"李家", "time":"晚上", "atmosphere":"温馨"},
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [{"type":"dialogue","character":"李建国","text":"凤兰，我想扩大规模，开分店。"},{"type":"dialogue","character":"刘凤兰","text":"你认真的？"},{"type":"dialogue","character":"李建国","text":"认真的！现在生意这么好，正是时候。"}]
 },
 {
 "scene_header":{"location":"街道", "time":"傍晚", "atmosphere":"宁静"},
 "scene_number":3,
 "characters":["李秀芳", "同学"],
 "content": [{"type":"dialogue","character":"同学","text":"秀芳，你父母的事业发展真快。"},{"type":"dialogue","character":"李秀芳","text":"是啊，他们都很努力。"},{"type":"emotion","description":"李秀芳为父母感到骄傲"}]
 }
 ]
}



### scripts/episode_16_script.json

{
 "episode_number":16,
 "title":"扩张的代价",
 "total_scenes":3,
 "scenes_detail": [
 {
 "scene_header":{"location":"新店址", "time":"白天", "atmosphere":"装修中"},
 "scene_number":1,
 "characters":["李建国", "工人"],
 "content": [{"type":"action","description":"李建国指挥工人装修新店"},{"type":"dialogue","character":"李建国","text":"这里要放大一点，显得气派。"},{"type":"action","description":"李建国眉飞色舞"}]
 },
 {
 "scene_header":{"location":"银行", "time":"上午", "atmosphere":"严肃"},
 "scene_number":2,
 "characters":["李建国", "银行员工"],
 "content": [{"type":"dialogue","character":"银行员工","text":"您的贷款申请需要时间。"},{"type":"action","description":"李建国有些着急"},{"type":"dialogue","character":"李建国","text":"好的好的，谢谢。"}]
 },
 {
 "scene_header":{"location":"李家", "time":"晚上", "atmosphere":"温馨"},
 "scene_number":3,
 "characters":["李建国", "刘凤兰"],
 "content": [{"type":"dialogue","character":"刘凤兰","text":"那笔贷款，你有把握吗？"},{"type":"dialogue","character":"李建国","text":"一定有把握的。"},{"type":"emotion","description":"李建国握住妻子的手，充满信心"}]
 }
 ]
}



### scripts/episode_1_script.json

{
 "episode_number":1,
 "total_scenes":3,
 "title":"通知到达",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"钢纺织厂大门口",
 "time":"白天",
 "atmosphere":"阴沉的天空，下班工人的麻木表情"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"action",
 "description":"工厂下班铃声响起，工人们陆续走出，李建国走在人群中，神情凝重地看着手中的纸张"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"今天这批 layoffs 的名单有你？（声音低沉）"
 },
 {
 "type":"dialogue", 
 "character":"刘凤兰",
 "text":"谁？（强装镇定，继续挎包跟在后面）"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"厂长的通知就在我手里，你还装什么？"
 },
 {
 "type":"action",
 "description":"刘凤兰终于停下脚步，周围的工人投来同情又好奇的目光"
 },
 {
 "type":"emotion",
 "description":"空气中弥漫着令人窒息的沉默，仿佛整个城市的命运都压在这两分钟里"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"走，回家再说。（做最后的坚强）"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家客厅",
 "time":"傍晚",
 "atmosphere":"昏暗的灯光，一张旧沙发，墙上的老日历停在某个日期"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"action",
 "description":"两人进门，父亲径直坐在老沙发，母亲去厨房倒水，水壶发出旧铁锈的噪音"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"没事，我能解决。（强装乐观，但声音干涩）"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"你天天这么说，厂已经裁了三批人了。我们还有儿子的学费，这个月的房租..."
 },
 {
 "type":"action",
 "description":"父亲沉默，低头看着自己的手，那双手曾经熟练地摆弄机械，现在却无处安放"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"我会想办法的。（声音罕见地软下来）"
 },
 {
 "type":"emotion",
 "description":"刘凤兰转身进厨房，背对丈夫的瞬间，肩膀开始微微颤抖"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家卧室",
 "time":"深夜",
 "atmosphere":"月光透过旧窗帘，照在空荡荡的大床和墙上挂着的全家福上"
 },
 "scene_number":3,
 "characters":["李建国"],
 "content": [
 {
 "type":"action",
 "description":"李建国独自坐在床边，手里攥着那个下岗通知，另一只手在旧皮箱里翻找着"
 },
 {
 "type":"action",
 "description":"他拿出几个旧盒子，里面是传家宝：爷爷留下的铜锁、母亲留下的玉镯、几本旧书"
 },
 {
 "type":"emotion",
 "description":"月光下，这些旧物显得格外珍贵。他意识到这是唯一的希望"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，对不起。（对着传家宝低语）但我得想办法活下去，得给这个家一条活路。"
 },
 {
 "type":"action",
 "description":"他在每件东西上轻轻摸了摸，像在做告别，然后将东西整齐地放进一个小包袱里"
 },
 {
 "type":"emotion",
 "description":"镜头扫过墙上的全家福，照片里的笑容与此刻的落寞形成鲜明对比"
 }
 ]
 }
 ]
}



### scripts/episode_2_script.json

{
 "episode_number":2,
 "total_scenes":3,
 "title":"第一桶金",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"夜市摊位",
 "time":"傍晚",
 "atmosphere":"热闹的夜市，各种叫卖声，昏黄的路灯"
 },
 "scene_number":1,
 "characters":["刘凤兰"],
 "content": [
 {
 "type":"action",
 "description":"刘凤兰推着一辆破旧的自行车来到摊位，展开一块洗得发白的蓝布"
 },
 {
 "type":"action",
 "description":"摊位上摆着自家的蔬菜，还有几十个鸡蛋。周围的摊贩大多是年轻人"
 },
 {
 "type":"dialogue",
 "character":"路人顾客",
 "text":"哟，这不是钢纺织厂的张师傅家那个...那个怎么称呼来着..."
 },
 {
 "type":"action",
 "description":"刘凤兰脸上挂着笑，熟练地称重、装袋"
 },
 {
 "type":"dialogue",
 "character":"顾客",
 "text":"不对，是那个下岗女工吧？居然在这里摆摊，真是丢人现眼。"
 },
 {
 "type":"action",
 "description":"周围的顾客都看过来，气氛有些尴尬。刘凤兰的笑容没有变"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"大姐您说笑了。现在这年头，靠自己双手挣饭吃，丢人现眼的该是那些吃闲饭的。"
 },
 {
 "type":"action",
 "description":"她快速称好一袋菜，抹去上面的尘土，递给顾客"
 },
 {
 "type":"dialogue",
 "character":"顾客",
 "text":"（尴尬）切吧，你这人嘴皮子利索的。下次还来。"
 },
 {
 "type":"emotion",
 "description":"夜市渐渐安静下去，刘凤兰收拾好东西，自行车上已经多了一个沉甸甸的篮子"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家客厅",
 "time":"晚上",
 "atmosphere":"家里昏暗的灯光，李建国不停地看着手表"
 },
 "scene_number":2,
 "characters":["刘凤兰", "李建国"],
 "content": [
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"你去夜市摆摊？（语气中带着压抑的怒气）你知道现在一个女人在夜市摆摊是什么意思吗？"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，你的那份工作也没了，我的工作也没了，总得有人撑下去。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"女人就该在家相夫教子！让你一个女人抛头露面，我李建国什么时候受过这份窝囊气？"
 },
 {
 "type":"action",
 "description":"刘凤兰没有争辩，默默地转身去倒水，水洒在了地上也不自知"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，这是你的家，我不强求。但我不能看着这个家垮掉。（声音颤抖但坚定）"
 },
 {
 "type":"emotion",
 "description":"李建国看着妻子的背影，拳头紧握，最终还是什么都没说"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家卧室",
 "time":"深夜",
 "atmosphere":"月光如水，照着刘凤兰正在缝补衣服的双手"
 },
 "scene_number":3,
 "characters":["刘凤兰", "李建国"],
 "content": [
 {
 "type":"action",
 "description":"李建国半夜醒来，看到刘凤兰还在昏黑的灯光下 busy with her hands"
 },
 {
 "type":"action",
 "description":"他借着月光，发现妻子手上全是细小的伤口——割菜时不小心划伤的"
 },
 {
 "type":"action",
 "description":"他想伸手摸一摸，手停在半空，最终还是没有落下"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰...您辛苦了。（声音沙哑）"
 },
 {
 "type":"action",
 "description":"这两个字他说出口时，眼眶有些发热。多少个夜晚，他都是一个人默默承受着压力"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"（停下手里活，转头看他）建国，这个月赚的够给你买件新衬衣了。别总是穿那件旧的。"
 },
 {
 "type":"emotion",
 "description":"月光下，刘凤兰的脸上带着疲惫但满足的笑容，李建国终于忍不住，从背后抱住了她"
 },
 {
 "type":"action",
 "description":"两个相拥的身影在月光下拉得很长，这是一个家庭重新出发的缩影"
 }
 ]
 }
 ]
}



### scripts/episode_3_script.json

{
 "episode_number":3,
 "total_scenes":3,
 "title":"重大选择",
 "scenes_detail": [
 {
 "scene_header":{
 "location":"社区礼堂",
 "time":"白天",
 "atmosphere":"简陋的礼堂布置，几张旧桌子，十几把椅子"
 },
 "scene_number":1,
 "characters":["刘凤兰", "李秀芳", "李建国", "赵桂芳", "米 rag 应该是 широкоragged group of people"],
 "content": [
 {
 "type":"action",
 "description":"十八岁的李秀芳站在简陋的礼堂中央，与周围华丽的成人礼形成鲜明对比"
 },
 {
 "type":"dialogue",
 "character":"赵桂芳",
 "text":"哟，这不是秀芳吗？今天是你成人礼吧？看你这身打扮，该不会是...自己在家过吧？"
 },
 {
 "type":"action",
 "description":"周围的亲戚朋友发出窃窃私语的笑声，刘凤兰上前手足无措地看着女儿"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"都是自己人，什么礼不礼的，一家人最重要。"
 },
 {
 "type":"dialogue",
 "character":"赵桂芳",
 "text":"凤兰姐，这年头谁还信这个？再说了，一个下岗女工的家庭，能给女儿办什么像样的成人礼？"
 },
 {
 "type":"action",
 "description":"李秀芳低着头，眼泪在眼眶里打转，但强忍着不让它落下来"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"阿姨，请您自重。这个家，比任何华丽的仪式都珍贵。"
 },
 {
 "type":"emotion",
 "description":"李秀芳的话让赵桂芳像被扇了一巴掌，周围的人都有些尴尬地转移了目光"
 }
 ]
 },
 {
 "scene_header":{
 "location":"医院病房",
 "time":"晚上",
 "atmosphere":"冰冷的医院走廊，消毒水的味道"
 },
 "scene_number":2,
 "characters":["李秀芳", "刘凤兰","医生"],
 "content": [
 {
 "type":"action",
 "description":"李秀芳在医院走廊里发抖，手里紧紧攥着一个皱巴巴的信封"
 },
 {
 "type":"dialogue",
 "character":"医生",
 "text":"刘凤兰的病需要长期调养，这一个月的药费至少要三千块。你们准备好了吗？"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"医生，我们可以等一等吗？我...我有一个办法。"
 },
 {
 "type":"action",
 "description":"她拉开包，里面是十几本写满笔记的课本——那是她高中时加倍努力的证明"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"这些书，我可以卖给学校资料室，或者挨家挨户็ราก ask，应该能凑够一部分。"
 },
 {
 "type":"emotion",
 "description":"她把课本分成了两堆，一笔记好的留给将来，几本破旧的准备卖出去"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"（喃喃自语）妈，我不会让你真的 LL 版ed的。我什么都愿意做。"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家客厅",
 "time":"深夜",
 "atmosphere":"昏黄的灯光下，桌上摊着那几本课本"
 },
 "scene_number":3,
 "characters":["李建国", "李秀芳"],
 "content": [
 {
 "type":"action",
 "description":"李建国无意间翻到秀芳的课第三代，看到了课本空白处的涂鸦"
 },
 {
 "type":"action",
 "description":"amazement，那不是普通的涂鸦，而是密密麻麻的小字：'为什么要读书？''谁能帮帮妈妈？''如果我 пош 体了，弟弟怎么办？'"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"这些...都是你写的？"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸爸，你看到了...我都说了吧？（声音沙哑）我都说了吧。"
 },
 {
 "type":"action",
 "description":"李建国看着女儿的笔记本，泪水夺眶而出。他一直以为女儿是叛逆期闹情绪"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"爸爸对不起你...都是爸爸不好..."
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸爸，别说了。我去想办法，行吗？我...我想辍学。"
 },
 {
 "type":"emotion",
 "description":"李建国突然站起，抱住女儿， father and daughter tears混合在一起"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"不，秀芳，爸爸想通了。你继续读，学费我想办法。就算去外面借高利贷，我也会还上的。"
 }
 ]
 }
 ]
}



### scripts/episode_4_script.json

{
 "episode_number":4,
 "total_scenes":3,
 "title":"风起南方",
 "scenes_detail": [
 {
 "scene_header":{
 "location":"李家客厅",
 "time":"晚上",
 "atmosphere":"烟雾缭绕，父子俩相对而坐"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，我想好了。我要在外面租个门面，开个小卖部。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"创业？（声音颤抖）建国，家里的钱已经不多了...这几千块是我们最后的家底了。万一赔了..."
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"正是因为不能赔，我才更要想办法。你看看现在的政策，改革开放了，遍地是机会。我肯定能行。"
 },
 {
 "type":"action",
 "description":"他把那叠零钱数了数，紧紧攥在手里"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"可是...你怎么向别人解释？别人看我们笑话怎么办？你不是说男人不能弯腰吗？"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"我现在就是要弯腰，为了这个家，我跪着也要往前走。你呢？要不要跟我一起？"
 },
 {
 "type":"action",
 "description":"刘凤兰沉默了很久，最后点了点头"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"我去，我陪你。只要这个家能站起来，我什么都愿意做。"
 }
 ]
 },
 {
 "scene_header":{
 "location":"街道旁的小卖部",
 "time":"白天",
 "atmosphere":"破旧的门面，周围是斑驳的墙壁，嘈杂的街道"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"action",
 "description":"李建国正在整理货架上的商品，动作小心翼翼，仿佛这些是稀世珍宝"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，你看，今天来的老客户ь族人这么多。你看这个。（展示报纸）深圳那边的政策还会包奖励呢。"
 },
 {
 "type":"action",
 "description":"他随手拿起一个旧相框，看到里面一张泛黄的照片"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"（喃喃自语）芳芳说她现在过得好...我能行，我也能行。（眼中的光芒）"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，你还在想她？"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"谁说她？我是想说，当年她那么勇敢，去深圳闯荡，我凭什么不能在这里开店？（声音低沉）"
 },
 {
 "type":"action",
 "description":"他擦了擦架子上的一盒方便面，眼中重新燃起了斗志"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"这个家，一定能在我们的努力下好起来的。现在我信了。"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家",
 "time":"深夜",
 "atmosphere":"昏黄的灯光，桌上堆满了账本和零钱"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"action",
 "description":"两人疲惫地坐在桌前，算着一天的收支"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"今天卖了两百多，能有个零头就不错了。（叹气)"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"生意是慢慢来的，凤兰。你看人最多的时候，不是一天就能做成的。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，我知道。我只是担心...万一..."
 },
 {
 "type":"action",
 "description":"李建国握住妻子的手，将她的头揽进怀里"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，别怕。就算最后一道难关，我们一起挺过去。当然赔得一无所有...你也还有这个家，这是我永远能给你的。"
 },
 {
 "type":"emotion",
 "description":"月光透过窗户洒在两人身上，他们依偎在一起，彼此支撑着度过这艰难的时刻"
 },
 {
 "type":"emotion",
 "description":"镜头缓缓移向窗外，看到远处有手电筒的光正在靠近门面"
 },
 {
 "type":"action",
 "description":"一只粗糙的大手正要推开门，门缝里传来他们的对话：
'明天工商局的来检查了，准备好了吗？'\n'嗯，一切都在计划中了。'
门被轻轻推开，光刺入昏暗的房间里"
 }
 ]
 }
]
}



### scripts/episode_5_script.json

{
 "episode_number":5,
 "total_scenes":3,
 "title":"风雨见真情",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"小卖部门口",
 "time":"白天",
 "atmosphere":"刺眼的手电筒光，严肃的执法氛围"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "执法人员", "赵桂芳"],
 "content": [
 {
 "type":"action",
 "description":"执法人员的到来打破了小卖部的平静，几个黑洞洞的手电筒照向店内"
 },
 {
 "type":"dialogue",
 "character":"执法人员",
 "text":"谁是负责人？例行检查，所有的经营许可证和进货单据拿出来。"
 },
 {
 "type":"action",
 "description":"李建国紧张地擦了擦额头上的冷汗，手忙脚乱地从柜台下翻找证件"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"同志，我们的证还在办，麻烦你们通融一下。"
 },
 {
 "type":"dialogue",
 "character":"赵桂芳",
 "text":"（在人群中冷笑）我说了私下的小道消息，那边绝对是过不了关的。"
 },
 {
 "type":"action",
 "description":"执法人员在检查单据，表情越来越严肃"
 },
 {
 "type":"dialogue",
 "character":"执法人员",
 "text":"这些进货单据不规范，而且你看这些食品有些临期的了。需要马上销毁，还要三千块罚款。"
 },
 {
 "type":"emotion",
 "description":"气氛更加紧张，李建国和刘凤兰的手紧紧躲在身侧"
 }
 ]
 },
 {
 "scene_header": {
 "location":"街道旁",
 "time":"下午",
 "atmosphere":"傍晚的天空，行人匆匆"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，三千块啊，这可是我们三的生活费了...我们要不要想办法求求情？"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，别急。食品虽然有点问题，但都是正规渠道进的，不至于这么严重吧？"
 },
 {
 "type":"action",
 "description":"李建国沉默，看着那几张单据，眼中满是不舍和恐慌"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"（咬牙）我再想想办法，实在不行...也只能凑钱了。"
 },
 {
 "type":"emotion",
 "description":"三千块，对他们来说是三个月的生活费。而不做选择的话，小卖部就得关门一个月"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"昏黄的灯光，一家人围坐在一起"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰", "李秀芳"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸，妈，老师说了学校有个老师认识工商局的人，说能帮忙处理这个事情。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"真的？太好了...这可是救命的希望！"
 },
 {
 "type":"action",
 "description":"李建国紧紧抱住女儿，眼中满是感激"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"（眼眶湿润）秀芳，你还小，不该为这些事操心的，真是辛苦你了。"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"妈，只要我们家能好起来，我什么都不怕。"
 },
 {
 "type":"emotion",
 "description":"一家三口紧紧相拥，在这个最困难的时候，亲情成了最大的支撑"
 }
 ]
 }
 ]
}



### scripts/episode_6_script.json

{
 "episode_number":6,
 "total_scenes":3,
 "title":"转机与挑战",
 "scenes_detail": [
 {
 "scene_header":{
 "location":"工商局办公室",
 "time":"白天",
 "atmosphere":"正式的办公环境，严肃的氛围"
 },
 "scene_number":1,
 "characters":["李建国", "执法人员"],
 "content": [
 {
 "type":"action",
 "description":"李建国带着老师给的联系，忐忑地走进工商局办公室"
 },
 {
 "type":"dialogue",
 "character":"执法人员",
 "text":"你就是那个老师的侄子？他说情况比较特殊，尽量人性化处理。"
 },
 {
 "type":"emotion",
 "description":"李建国松了一口气，心中的石头落了一半"
 },
 {
 "type":"dialogue",
 "character":"执法人员",
 "text":"不过，罚款还是要的，不是三千，但我们可以少一些，降到一千五。而且你可以选择一周内办理手续，而不是立即关门。"
 },
 {
 "type":"action",
 "description":"李建国眼睛一亮，连连点头"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"谢谢！谢谢！我会马上去办的，一定不会让你们失望。"
 }
 ]
 },
 {
 "scene_header":{
 "location":"小卖部",
 "time":"傍晚",
 "atmosphere":"关门后的寂静"
 },
 "scene_number":2,
 "characters":["刘凤兰", "李建国"],
 "content": [
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"（紧张地看着丈夫）怎么样？结果怎么样？"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"成了！凤兰，成了！他们说可以免掉一部分罚款，只要我们一周内把手续补齐。"
 },
 {
 "type":"action",
 "description":"刘凤兰激动地抱住丈夫，眼泪夺眶而出"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"太好了...太好了...明天我们去把手续办了，就安全了。"
 },
 {
 "type":"emotion",
 "description":"夫妻俩紧紧相拥，这是我们历经困难后收获的第一个好消息"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨的灯光"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰", "李秀芳"],
 "content": [
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"秀芳，这次真是多亏了你。没有你的帮助，我们这个小卖部可能就完了。"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸，你说什么话，咱们是一家人。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"没错，这个家现在最该感谢的就是秀芳。以后有好吃的好穿的，秀芳肯定是第一个。"
 },
 {
 "type":"emotion",
 "description":"李秀芳看着父母，眼中闪烁着幸福的光芒，这个家正在慢慢好起来"
 }
 ]
 }
 ]
}



### scripts/episode_7_script.json

{
 "episode_number":7,
 "total_scenes":3,
 "title":"小卖部的故事",
 "scenes_detail": [
 {
 "scene_header":{
 "location":"小卖部",
 "time":"白天",
 "atmosphere":"生意兴隆，顾客络绎不舍"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "顾客们"],
 "content": [
 {
 "type":"action",
 "description":"小卖部里顾客络绎不绝，李建国忙得满头大汗"
 },
 {
 "type":"dialogue",
 "character":"顾客甲",
 "text":"老李，你这店里东西越来越全了，比超市还方便。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"那是，你们要啥都有，我尽量把你们需求都满足。"
 },
 {
 "type":"dialogue",
 "character":"顾客乙",
 "text":"可不是，现在的李老板，跟以前那个只会修机器的李建国完全不一样了。"
 },
 {
 "type":"action",
 "description":"李建国听了满意地笑了"
 }
 ]
 },
 {
 "scene_header":{
 "location":"街道",
 "time":" evening",
 "atmosphere":"下班的人和熙熙攘攘的街道"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，你看这些天生意越来越好，咱们这个决定真的做对了。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"是啊，这几天算下来，比过去了多少播出还要多啊。"
 },
 {
 "type":"action",
 "description":"李建国看着忙碌的小吃店，心中充满自信"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，咱们终于撑过来了。接下来就好了，每一天都是更好的。"
 }
 ]
 },
 {
 "scene_header":{
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨的灯光"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰", "李秀芳"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸，妈，我今天刚从学校回来，看到咱们小卖部简直换了个人一样。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"哈哈，你这孩子，怎么夸起老爸了。"
 },
 {
 "type":"action",
 "description":"刘凤兰端着一盘热腾腾的饭菜上桌"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"好了，吃饭了。今天庆祝小卖部大获成功。"
 },
 {
 "type":"emotion",
 "description":"一家人围坐在一起，其乐融融，是这段时间来最温馨的时刻"
 }
 ]
 }
 ]
}



### scripts/episode_8_script.json

{
 "episode_number":8,
 "total_scenes":3,
 "title":"牺牲的日常",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"小卖部",
 "time":"清晨",
 "atmosphere":"黎明的微光刚照进来，街道还很安静"
 },
 "scene_number":1,
 "characters":["刘凤兰"],
 "content": [
 {
 "type":"action",
 "description":"刘凤兰独自起床，整理门前还有些凌乱的桌椅和货物"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"（深呼吸）又是新的一天，今天一定要更努力一点。"
 },
 {
 "type":"action",
 "description":"她活动了一下酸痛的腰背，开始清扫店面"
 },
 {
 "type":"emotion",
 "description":" essere tutto ché il mondo cerca, con un cuore che ciò traduce,—她早已习惯一个人早起整理店面的时间，不再觉得独自工作是一种automaticité"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨但安静的灯光"
 },
 "scene_number":2,
 "characters":["李建国", "刘凤兰"],
 "content": [
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"建国，我最近太累了，晚上总是起不来，白天的时候偶尔要偷偷休息一下。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"凤兰，你辛苦了，但是这样的日子快结束了，再坚持一下。"
 },
 {
 "type":"action",
 "description":"李建国轻轻帮刘凤兰按揉酸痛的手臂"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"你在家里照顾，尽量减少点工作量就行。外面的客人我来接待。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"不行啊，建国，我铺开来的事情不能精湛自己内部晚上给您接里头 。"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李秀芳的学校",
 "time":"白天",
 "atmosphere":"学校的走廊"
 },
 "scene_number":3,
 "characters":["李秀芳", "同学们"],
 "content": [
 {
 "type":"action",
 "description":"李秀芳站在校门口，看着破旧的校舍，思考着自己的 future"
 },
 {
 "type":"dialogue",
 "character":"同学甲",
 "text":"秀芳，你爸妈现在怎么样了？听说生意还在做？"
 },
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"嗯，还在做，但最近赚得不多。我不打算辍学，我继续瞒宇 实在想了很多办法 work赚钱。"
 },
 {
 "type":"dialogue",
 "character":"同学乙",
 "text":"秀芳，你真的了不起，父母这样困难，你还坚持读书。"
 },
 {
 "type":"emotion",
 "description":"李秀芳轻轻点了点头，眼中满是坚定"
 }
 ]
 }
 ]
}



### scripts/episode_9_script.json

{
 "episode_number":9,
 "total_scenes":3,
 "title":"艰难的进步",
 "scenes_detail": [
 {
 "scene_header": {
 "location":"小卖部",
 "time":"白天",
 "atmosphere":"生意 Közeledik"
 },
 "scene_number":1,
 "characters":["李建国", "刘凤兰", "顾客"],
 "content": [
 {
 "type":"action",
 "description":"Li Fèng Lán's store 现在更离不开这个小小的站点，胜利从难处购买 nosso"
 },
 {
 "type":"dialogue",
 "character":"顾客",
 "text":"李老板，你这品种越来越多了，价格也实惠，大家都爱来你的店。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"谢了张阿姨，您能来捧场我就感激不尽了。"
 },
 {
 "type":"action",
 "description":"李建国忙碌得满脸是汗，但因效果人而感到高兴"
 },
 {
 "type":"emotion",
 "description":"看到提栏 lighter 如期待到家的映照，他抱着更多希望清AndGet pacing"
 }
 ]
 },
 {
 "scene_header": {
 "location":"街道旁",
 "time":"傍晚",
 "atmosphere":"多家城镇的小游行"
 },
 "scene_number":2,
 "characters":["李建国"],
 "content": [
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"（自言自语）这生意做得真好啊，咱们终于要登上谈判桌了。"
 },
 {
 "type":"action",
 "description":"他看着渐暗的光线，心中的喜悦自然脱口而出"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"明天再进一批货，把品种再大一点，生意肯定更好。"
 }
 ]
 },
 {
 "scene_header": {
 "location":"李家",
 "time":"晚上",
 "atmosphere":"温馨的家庭氛围"
 },
 "scene_number":3,
 "characters":["李建国", "刘凤兰", "李秀芳"],
 "content": [
 {
 "type":"dialogue",
 "character":"李秀芳",
 "text":"爸，最近生意好吗？在学校的时候，我看到好多同学亲口 affirmation 你的小卖部很有名。"
 },
 {
 "type":"dialogue",
 "character":"李建国",
 "text":"好，特别好，几乎 everything。Tekla solving 生意的匹配改善状况。"
 },
 {
 "type":"dialogue",
 "character":"刘凤兰",
 "text":"好，HTTPRequestOperation 就搬来 cuatro más alla saborbs，会更丰富，这样做的人会更多。"
 },
 {
 "type":"emotion",
 "description":"一家人围坐在灯光下，谈笑happy，这个家庭已经成为VIC归属Vequation"
 }
 ]
 }
 ]
}



# 当前任务

请撰写：第17集剧本，包含场景描述、角色对话、镜头指示
