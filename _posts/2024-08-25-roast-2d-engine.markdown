---
layout: post
title: "我开发了一款 2D 游戏引擎并用它参加 GMTK Game Jam"
data: 2024-08-25 17:24
tags: 中文 Roast2D
---

## Roast2D

[Roast2D][roast-2d] 是一款受 [high_impact][high_impact] 引擎启发，由 Rust 编写的适合快速开发的 2D 游戏引擎。 Roast2D 内置简单的物理碰撞检测，支持 [LDTK][ldtk] 关卡编辑器，并且支持编译为 WASM 在浏览器中运行。

[Roast2D source code][roast-2d]

## 示例游戏

Baloon Game

<img src="/assets/images/Roast2D/balloon-2.gif" width="240" height="240" />

* [Game on itch.io][balloon-game]
* [Source code on GitHub][balloon-repo]

Demo Brick

<img src="/assets/images/Roast2D/brick-1.gif" width="240" height="240" />

* [Source code on GitHub][brick-demo]


这篇文章分享了我开发 Roast2D 的初衷以及使用该引擎参加 GMTK Game Jam 的过程。

## 游戏开发之梦

每个喜欢打游戏的程序员都想过要自己开发游戏，当这个想法再次浮现时，我决定参加一次 Game Jam。如果我喜欢玩游戏，对游戏有自己的品味和理解，为什么不试着做一款呢？

我开始在 GitHub 搜索 "Rust game engine"。

打开了 Bevy 教程，开始学习 Sprite，Tilemap, UINode 等概念，下载 Aseprite 以及 LDTK 等游戏制作工具。随着时间过去了一年，我更加的了解了游戏开发以及引擎技术，我尝试绘制出简单的 2D sprite 并增加移动等操作，我尝试过在 LDTK 中用 tilemap 制作地图，但从来没有做出像样的游戏 Demo，也没有参加过 Game Jam。

## 受到 high_impact 的启发

就在我快要忘记参加一次 Game Jam 这个想法时，我看到了一篇关于 [high_impact 引擎的文章][high_impact_article] ，作者介绍了如何用 C 去重写 10 多年前 JavaScript 实现的 impact 引擎。

high_impact 简单的设计，以及作者对使用简单技术的追求触动了我。我反复看了多遍，意识到远星物语正是使用文章中提到的原版 impact 引擎开发的。我正好玩过这款游戏，这让我产生了更多的兴趣去阅读 high_impact 的代码。

high_impact 代码比我想象的简单很多，但也包含了一些我不熟悉的 C 语言技巧。

high_impact 提供 Entity 结构来表示游戏中的对象，结构中包含 velocity, accel, gravity, pos, health 等字段，这些字段定义了大部分的游戏对象都需要的属性。引擎会根据 Entity 这些属性去更新位置，检查碰撞逻辑，调用回调方法等等。

游戏代码需要通过一个巨大的 union 类型来定义所有的 Entity Type，如玩家，敌人，投射物等等。

``` c
// https://github.com/phoboslab/high_biolab/blob/master/src/high_impact.h#L114
union {
    // ...
	struct {
		float high_jump_time;
		float idle_time;
		bool flip;
		bool can_jump;
		bool is_idle;
	} player;

	struct {
		anim_def_t *anim_hit;
		bool has_hit;
		bool flip;
	} projectile;	
    // ...
}
```

就像这样，把 player, projectile 以及其他的 Entity 都定义在这个巨大的 union 结构中，而这个 union 结构会被保存在 Entity struct 的最后一个字段中。

这样处理看起来粗糙，但确实是一个简单的做法，所有的 Entity Type 都是通过 union 定义的，他们具有同样的大小，可以把所有 Entities 保存在一个数组中。

我虽然不是专业的游戏开发者，但我了解过 ECS，我知道这样做的性能会打折扣，Entity 结构字段太多了，数据没法全部放进 CPU cache 中，在引擎更新 Entity 时 CPU 需要多次的从内存中重新加载数据，对性能会有影响...而 ECS 可以把数据存储的更紧凑！

但我欣赏这种简单易懂的代码，我可以直接去看 Player 或者 Enemy 中定义的 `update` 逻辑以及 `draw` 逻辑，而不是先去了解 Query, Stage 等等概念再去 Systems 中翻找真正起作用的代码。用一个超大的 union 定义 Entity 的做法任何编程语言教程都不会推荐，但是这样做可以使引擎的逻辑非常简单。

我发现过去的时间我迷失在了学习种种的抽象概念，但是从未接近我真正想要做的事情。

或者复杂的技术有独特的价值，但是确实不是我需要的。我需要使用简单的，我能理解的技术去参加一次 Game Jam，而不是投入到我无法完全掌握的复杂技术中。我喜欢 high_impact 的简单直接，可以直接去阅读，修改代码，而不是在一层层抽象中迷失。

我决定开发一款类似的引擎。

## 好的程序员偷代码

那么为什么需要自己开发一个引擎，而不是直接用 high_impact？仅仅是 Rewrite everything in Rust 主义？

首先容我辩解下，我欣赏 C 的简单明了，快速的编译，可移植性。如果 C 程序有数组越界检查以及 module 系统，最好再加上一个类似 cargo 的工具，我会很愿意使用。但我并没有长期的使用 C 的经验，我不希望花费时间去学习 Makefile 写法以及去用我不熟悉的工具 debug 段错误。

相比 C ，我厌恶 Rust 的繁琐以及与编译器无意义的搏斗，但是 cargo 很好用，可以方便的管理依赖。而且凭借我对 Rust 的熟悉，我相信可以更快的完成这个任务。

另一个理由更可信一点：我就是想要写一个引擎。

我打算大致上模仿 high_impact 的设计与实现，融入我的偏好来快速的制作一个简单的 2D 引擎 [Roast2D][roast-2d]。

## 定义 Entity

Entity 代表游戏中的实体，比如主角，敌人，道具，陷阱都是 Entity。

Roast2D 中也定义了一个通用的 Entity 结构体，里面有 velocity, accerate, pos, health 等属性， 引擎在游戏的 loop update 中会读取这些值，更新 Entity 位置,根据物理特性去检查碰撞，移除 health 为 0 的 Entity 等。

前文提到 high_impact 使用 union 结构去扩展 Entity，这样不同类型的 Entity 大小一致，可以统一的保存在数组中。而在 Roast2D 中我们使用 trait object 来实现目的, 内存由 Rust global allocator 管理，并没有本质上的不同。

Entity 结构中的 `instance` 字段用来保存 trait object。Rust 中的 trait object 有点类似 OOP 语言中的对象，可以理解成数据加上 vtable，我们通过 `instance` 可以调用 EntityType 中定义的方法。

``` rust
pub struct Entity {
    pub ent_ref: EntityRef,
    pub ent_type: EntityTypeId,
    /// ... ignore some fields
    pub(crate) instance: Option<Box<dyn EntityType>>,
}

pub trait EntityType: DynClone {
    /// Load an entity type
    fn load(_eng: &mut Engine) -> Self
    where
        Self: Sized;

    /// Initialize an entity
    fn init(&mut self, _eng: &mut Engine, _ent: &mut Entity) {}

    /// Update callback is called before the entity_base_update
    fn update(&mut self, _eng: &mut Engine, _ent: &mut Entity) {}

    // Draw entity anim
    fn draw(&self, eng: &mut Engine, ent: &mut Entity, viewport: Vec2) {
        if let Some(anim) = ent.anim.as_mut() {
            anim.draw(&mut eng.render, (ent.pos - viewport) - ent.offset);
        }
    }

    // ... some functions are ignored
}
```

定义代码如下，游戏需要为每种 Entity 定义 struct 结构，并对 struct 实现 `EntityType`。

我们把 `Engine` 以及 `Entity` 作为参数传到了接口中，这样方法实现中可以直接读写当前的 Entity。效果很像是在 C 中实现 OOP 方法时需要把 `self` 作为参数传递到方法中，在 Rust 中并不常用，但是简单，而且易于理解。

``` rust
#[derive(Clone)]
pub struct Player {
    score: usize,
    texture: Handle,
}

impl EntityType for Player {
    fn load(eng: &mut Engine) -> Self {
        let texture = eng.load("player.png");
        Player{ score: 0, texture }
    }

    fn init(_eng: &mut Engine, ent: &mut Entity) {
        ent.size = Vec2::spalt(32.0);
        //... setup entity
    }

    //...
}
```

`load` 方法只会被调用一次，用来加载 Entity 需要的资源并构造实例。我选择把 `load` 返回的实例保存下载。当生成 Entity 时，其实是在 clone `load` 返回的实例。这种做法比较偷懒，另一个选择是类似 Bevy 那样用宏实现 Rust struct 的 reflect 功能，那意味着我需要连续在半夜工作几个月。从接口上看不出什么区别，因此我觉得目前的方式已经足够好了。

``` rust
/// Add Entity Type, Player#load is called
eng.add_entity_type::<Player>();
/// Spawn player instance, Player#init is called
eng.spawn::<Player>(Vec2::splat(40.0));
```

## Collision detection

Collision detection 基本只是把 high_impact 的代码改成 Rust，没有修改逻辑，这里有篇文章很好的解释了 [sweep and prune 算法][sweep-and-prune]

关于斜坡部分的代码太复杂，而且暂时用不上，于是我跳过了这一部分，只支持平面。

## SDL2 和 WASM

平台相关的代码反而简单的多，核心需求是能在不同的平台上画出长方形，并在其中显示像素，我们用简单的 trait 来抽象这些方法。

``` rust
pub trait Platform {
    /// Return seconds since game started
    fn now(&mut self) -> f32;
    fn prepare_frame(&mut self);
    fn end_frame(&mut self);
    fn cleanup(&mut self);
    fn draw(
        &mut self,
        texture: &Handle,
        color: Color,
        pos: Vec2,
        size: Vec2,
        uv_offset: Vec2,
        uv_size: Option<Vec2>,
        angle: f32,
        flip_x: bool,
        flip_y: bool,
    );
    fn create_texture(&mut self, handle: Handle, data: Vec<u8>, size: UVec2);
    fn remove_texture(&mut self, handle_id: HandleId);
    #[allow(async_fn_in_trait)]
    async fn run<Setup: FnOnce(&mut Engine)>(
        title: String,
        width: u32,
        height: u32,
        vsync: bool,
        setup: Setup,
    ) -> Result<()>
    where
        Self: Sized;
}
```

起初我决定只支持 SDL2 backend，但是随后发现 sdl2 rust crate 有很多小问题，比如无法编译到 `wasm32-unknown-unknown` target，这意味着我们的游戏无法运行在浏览器上。

于是我决定增加 Web backend 支持，使用 Web canvas 接口实现 `Platform`。

在 Rust 中可以通过 `wasm-bindgen` crate 直接调用 canvas 接口，体验很好，基本 JavaScript 能做到的都可以直接用 Rust 做到，甚至不需要考虑 lifetime ！所有的 Dom 对象都是可变的!

Web backend 本质是在调用 canvas 的 drawImage 接口去绘制图像，我花了很多时间处理 Canvas 中出现在 tile 边缘的神秘白线，剩下的事情都比较顺利。

在实现 Web backend 时，我已经有了一部分可以运行游戏代码，一边实现简单的接口一边可以看着游戏逐渐跑起来，是一种很神奇的体验。high_impact 没有使用 canvas API，所以这部分代码无法 copy，需要我自己思考，有种骑自行车第一次拿掉了辅助轮的新鲜感。

## Asset loading 资源管理

因为增加了 Web 支持, 加载图片等资源时没办法直接用简单的文件 io, 我决定模仿 Bevy 中资源加载的方式，提供一个 AssetManager 以及 load 接口，接口会立刻返回一个 Handle 实例表示对资源的引用，Handle 中仅仅保存了一个 ID 代表资源。

``` rust
#[derive(Debug)]
pub enum AssetType {
    Raw,
    Texture,
}

impl AssetManager {
    pub fn load<P: AsRef<Path>>(&mut self, path: P, asset_type: AssetType) -> Handle {
        //...
    }
    pub fn get_raw(&self, handle: &Handle) -> Option<&Vec<u8>> {
        //...
    }
    pub(crate) async fn fetch(&mut self) -> Result<Vec<FetchedTask>> {
        //...
    }
}
```

当调用 `load` 加载 Texture 类型的资源时，资源加载完成后，引擎会自动调用 `Platform#create_texture` 创建不同平台下的 Texture，在 SDL2 中会创建 `SDLTexture`，而在 Web 中会创建一个 `OffscreenCanvas`。

当调用 `load` 加载 Raw 类型的资源时，我们仅仅保存成 `Vec<u8>`, 需要游戏代码通过 `get_raw` 接口从引擎获取结果并继续处理资源。

AssetManager 的 `fetch` 会在每一帧被调用，接口会检查是否有请求的资源，如果有则尝试加载。在 Web 中 fetch asset 通过 web worker 完成，在非 Web 环境中则通过标准库的 file io 完成。

游戏代码中需要保存 `load` 返回的 Handle 来引用资源

``` rust
let handle = eng.assets.load_texture("demo.png");
let sprite = Sprite::new(handle, UVec2::splat(32));
```

当 handle 的所有引用都被删除时，AssetManager 会释放资源，如果是 texture 则会调用 `Platform#remove_texture`：

``` rust
impl Drop for StrongHandle {
    fn drop(&mut self) {
        let _ = self.drop_sender.send(DropEvent(self.id));
    }
}

impl AssetManager {
    pub(crate) async fn fetch(&mut self) -> Result<Vec<FetchedTask>> {
        // ...
        // remove dropped assets
        while let Ok(event) = self.receiver.try_recv() {
            self.assets.remove(&event.0);
            let fetched_task = FetchedTask::RemoveTexture { handle: event.0 };
            tasks.push(fetched_task);
        }
        // ...
    }
}
```

代码很大程度上参考了 Bevy, 但是我只实现了非常简化的版本，去掉了和 reflect 相关的部分，并且尽量去掉了多余的抽象层。

## Sound 音频接口

我不熟悉播放音频的接口该如何设计，因此选择不把音频集成到引擎中，不过游戏代码中可以直接使用 [kira][kira] crate 来跨平台支持音频。游戏中可以通过 [Roast2D][roast-2d] 提供的 AssetManager 接口加载音频资源，并在资源加载完毕后交给 kira 处理。

这里留下了[示例代码][kira-example]，在每次播放音频会去检查是否已经有缓存文件，如果没有则尝试检查 AssetManager 中资源是否加载。

``` rust
match self.sounds_data.get(handle) {
    Some(data) => {
        log::debug!("Get sound {sound:?} cached");
        Some(data.to_owned())
    }
    None => {
        let Some(raw) = eng.assets.get_raw(handle).cloned() else {
            log::debug!("Get sound {sound:?} not ready");
            return None;
        };
        log::debug!("Get sound {sound:?} done");
        let data = StaticSoundData::from_media_source(Cursor::new(raw)).unwrap();
        self.sounds_data.insert(handle.to_owned(), data.clone());
        Some(data)
    }
}
```

## LDTK 关卡编辑器

[LDTK][ldtk] 是一个开源的游戏关卡编辑器，我尝试过 LDTK 并感觉良好，因此我决定让 Roast2D 支持 LDTK。

LDTK 并不和特定的游戏引擎绑定，在 LDTK 中支持定义 Entity，World, Level, Layer 等常用的概念，并支持导入 tileset 等资源，LDTK 最终输出一个后缀为 `ldtk` 的 JSON 文件。

我们解析这个 JSON 文件并让 Roast2D 正确的理解需要加载的 entity, tileset, tile 位置即可。

使用 Roast2D 和 LDTK 时有几个约定：

1. 每个关卡可以创建一个 Collision layer, 如果 layer 类型为 IntGrid, 名称为 `Collision`。Roast2D 会尝试将其作为 Collision Map 解析，`0` 代表 tile 无碰撞，`1` 代表 tile 会产生碰撞。
2. 每个关卡可以创建一个 Entities layer, layer 的类型为 Entity, 名称为 `Entities`，layer 中包含的 Entity 名称必须和 Roast2D 中定义的类型名称一致，这样 Roast2D 才可以正确的 spawn 对应 Entity。

<img src="/assets/images/Roast2D/level-editing.png" width="600"/>

## GMTK-2024 Game Jam

GMTK 2024 的主题是 scale, 最简单的理解是尺寸上的变化。

经过了一段时间的思考，我决定用平台跳跃游戏来阐释，主角的形象是一个气球，玩家可以控制充气以及放气，当充气时主角可以浮起来，体重变轻跳的更高，当放气时主角会被气流吹动或者很大的加速度。

我很快完成了机制的编码，并画了像素图形。在提交结束当天，我设计了提示玩家操作的提示牌。

<img src="/assets/images/Roast2D/balloon-3.gif" width="240" height="240"/>

截止到当前的时间，我的游戏获得了 6 个 review。

我的目标是 10 个 review，在看到 GMTK-2024 提交数有 7K 多款游戏时，我下调了预期，有 5 个 review 就满意了，算是达成了目标。

## 总结

快速的从开源项目 copy 代码是非常高效的学习方式，我之前读代码时会盯着代码看，但远不如直接把代码复制过来，修改并尝试编译，遇到问题时重新阅读来的高效。

参加 Game Jam 并且快速的设计、制作游戏原型很有意思，这种 Code Rush 会让人感觉到充满了生产力，我会继续参加 Game Jam，当然下次会选择规模更小的 Game Jam，我猜测在小型的 Game Jam 中提交游戏会有更多概率被 Review 到。

[roast-2d]: https://github.com/jjyr/roast2d
[high_impact]: https://github.com/phoboslab/high_impact
[high_impact_article]: https://phoboslab.org/log/2024/08/high_impact
[ldtk]: https://ldtk.io/
[sweep-and-prune]: https://leanrada.com/notes/sweep-and-prune/
[kira-example]: https://github.com/jjyr/balloon-game/blob/835ea2f0fb768d944484fe33b8f662a4a1e4daf7/src/lib.rs#L643-L759
[itch]: https://itch.io/
[kira]: https://github.com/tesselode/kira
[balloon-game]: https://jijiy.itch.io/gmtk-2024-balloon-advanture
[balloon-repo]: https://github.com/jjyr/balloon_game
[brick-demo]: https://github.com/jjyr/roast2d/blob/master/examples/demo.rs
