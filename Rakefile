site_dir = "_site"
deploy_repo = "git@github.com:jjyr/jjyr.github.com.git"
deploy_branch = "master"

desc "Default deploy task"
task :deploy do

  puts "## Remove old site..."
  rm_rf site_dir

  puts "## Generating..."
  system("bundle exec jekyll build")

  puts "Compressing images..."
  Dir.glob("#{site_dir}/**/*.*") do |item|
    next if item == '.' or item == '..'

    ext = File.extname(item)


    case ext.downcase
    when '.png'
      system("optipng #{item}")
    when '.jpg','.jpeg'
      system("jpegoptim --strip-all --max=90 #{item}")
    end
  end 

  puts "## Prepare pushing to github" 
  cd "#{site_dir}" do
    system "git init"
    system "git add ."
    system "git commit -m \"Deploy #{Time.now}\""
    system "git remote add origin #{deploy_repo}"
    system "git push -f origin master"
  end
end

desc "create new post"
task :new_post, :title, :filename do |t, args|
  require 'ruby-pinyin'

  unless args[:title]
    puts "title cannot blank"
    p args
    exit 1
  end
  time = Time.now
  title_pinyin = PinYin.of_string(args[:title]).join('-')
  filename = "./_posts/#{time.strftime "%Y-%m-%d"}-#{title_pinyin}.markdown"
  File.open(filename, "w") do |f|
    f.write <<HEAD
---
layout: post
title: "#{args[:title]}"
data: #{time.strftime "%Y-%m-%d %H:%M"}
comments: true
---
HEAD
  end
  puts "created post #{filename}"
end
