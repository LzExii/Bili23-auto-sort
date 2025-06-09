import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件自动归类工具")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground="#2c3e50")
        self.style.configure("Status.TLabel", font=("Arial", 9), foreground="#555555")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        self.title_label = ttk.Label(
            self.main_frame, 
            text="文件自动归类工具", 
            style="Title.TLabel"
        )
        self.title_label.pack(pady=(0, 20))
        
        # 说明文本
        instruction_text = (
            "本工具用于自动整理MP4文件：\n"
            "1. 文件格式应为：数字 - 《文件名》备注.mp4\n"
            "2. 文件将被移动到以《文件名》命名的文件夹中\n"
            "3. 支持处理如 'A', 'A 第一季', 'A剧场版' 等不同名称\n"
            "4. 只处理选中的主文件夹，不会修改子文件夹内容"
        )
        self.instruction_label = ttk.Label(
            self.main_frame, 
            text=instruction_text,
            justify=tk.LEFT
        )
        self.instruction_label.pack(pady=(0, 20), fill=tk.X)
        
        # 文件夹选择区域
        folder_frame = ttk.Frame(self.main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_label = ttk.Label(folder_frame, text="选择文件夹:")
        self.folder_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_button = ttk.Button(folder_frame, text="浏览...", command=self.browse_folder)
        self.browse_button.pack(side=tk.LEFT)
        
        # 整理按钮
        self.organize_button = ttk.Button(
            self.main_frame, 
            text="开始整理文件", 
            command=self.organize_files,
            state=tk.DISABLED
        )
        self.organize_button.pack(pady=20)
        
        # 日志区域
        log_frame = ttk.Frame(self.main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_label = ttk.Label(log_frame, text="操作日志:")
        self.log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = tk.Text(
            log_frame, 
            height=10,
            wrap=tk.WORD,
            bg="white",
            bd=1,
            relief=tk.SOLID
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 - 请选择文件夹")
        self.status_label = ttk.Label(
            root, 
            textvariable=self.status_var,
            style="Status.TLabel",
            anchor=tk.W,
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定事件
        self.folder_path.trace_add("write", self.check_folder_path)
    
    def browse_folder(self):
        """打开文件夹选择对话框"""
        folder_selected = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.add_log(f"已选择文件夹: {folder_selected}")
    
    def check_folder_path(self, *args):
        """检查文件夹路径是否有效"""
        if os.path.isdir(self.folder_path.get()):
            self.organize_button.config(state=tk.NORMAL)
            self.status_var.set(f"就绪 - 可以整理文件夹: {self.folder_path.get()}")
        else:
            self.organize_button.config(state=tk.DISABLED)
            self.status_var.set("就绪 - 请选择有效的文件夹")
    
    def organize_files(self):
        """整理文件的主函数"""
        folder_path = self.folder_path.get()
        if not os.path.isdir(folder_path):
            messagebox.showerror("错误", "选择的文件夹不存在！")
            return
        
        self.add_log("开始整理文件...")
        self.status_var.set("整理中...")
        self.root.update()
        
        try:
            # 获取文件夹中的所有文件（不包含子文件夹）
            files = [f for f in os.listdir(folder_path) 
                     if os.path.isfile(os.path.join(folder_path, f)) 
                     and f.lower().endswith('.mp4')]
            
            if not files:
                self.add_log("没有找到MP4文件")
                self.status_var.set("完成 - 没有找到MP4文件")
                return
            
            total_files = len(files)
            processed_files = 0
            
            for filename in files:
                # 匹配格式：数字 - 《文件名》备注.mp4
                # 修正正则表达式以匹配实际文件名格式
                match = re.match(r'^\d+\s*-\s*《([^》]+)》', filename)
                if not match:
                    self.add_log(f"跳过不符合格式的文件: {filename}")
                    continue
                
                # 提取文件名部分（《》内的内容）
                folder_name = match.group(1).strip()
                
                # 创建目标文件夹（如果不存在）
                target_dir = os.path.join(folder_path, folder_name)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    self.add_log(f"创建文件夹: {folder_name}")
                
                # 移动文件
                src_path = os.path.join(folder_path, filename)
                dst_path = os.path.join(target_dir, filename)
                
                # 处理目标文件名冲突
                counter = 1
                while os.path.exists(dst_path):
                    base_name, ext = os.path.splitext(filename)
                    new_filename = f"{base_name}_{counter}{ext}"
                    dst_path = os.path.join(target_dir, new_filename)
                    counter += 1
                
                shutil.move(src_path, dst_path)
                self.add_log(f"已移动: {filename} -> {os.path.join(folder_name, os.path.basename(dst_path))}")
                processed_files += 1
            
            self.add_log(f"整理完成! 共处理 {processed_files}/{total_files} 个文件")
            self.status_var.set(f"完成 - 处理了 {processed_files} 个文件")
            messagebox.showinfo("完成", f"文件整理完成!\n共处理 {processed_files} 个文件")
            
        except Exception as e:
            self.add_log(f"发生错误: {str(e)}")
            self.status_var.set("错误 - 操作失败")
            messagebox.showerror("错误", f"整理文件时发生错误:\n{str(e)}")
    
    def add_log(self, message):
        """添加日志到文本区域"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()